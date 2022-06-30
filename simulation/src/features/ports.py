"""
   Copyright (C) 2022 Graz University of Technology. All rights reserved.

   Author: Christoph Leitner

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at:

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""


import pandas as pd
import numpy as np


def frequency_spectrum(F):
    return np.arange(F[0] * 10 ** 6, F[1] * 10 ** 6, 1 * 10 ** 6, dtype=int)


# PROPAGATION CONSTANT (gamma)
#
# gamma = alpha + 1j*beta
#
# alpha = attenuation constant (amplitude loss per length),
# beta = phase constant (phase change per length)
#
# Lossless transmission line: alpha = 0, gamma = 1j*beta
#
# beta = 2pi / lambda = 2pi * f / sos
#
def calculate_beta(f, v):
    return (2 * np.pi * f) / v


def parallel_circuit_impedance(Z1, Z2):
    return (Z1 * Z2) / (Z1 + Z2)




class acoustic_transmission_line():
    def __init__(self, transducer=None, init=None, fband=None):

        self._transducer_stack = transducer.stack
        self._transducer_stack_idx = transducer.midx_stack
        self._Z0 = init
        self._frequency_band = frequency_spectrum(fband)

        self._speed_of_sound = transducer.material.loc[:, ['v']].T
        self._transmission_line_length = transducer.geometry.loc[:, ['Thickness']].T


######### Calculate Transmission Line
        #
        self._Z_Top_transmission_line = self.transform_Top2Bottom(char_impedance=self._Z0.loc[:, (slice(None), ['Top'], slice(None))],
                                                                  length=self._transmission_line_length.loc[:, (slice(None), ['Top'], slice(None))],
                                                                  frequency=self._frequency_band,
                                                                  sos=self._speed_of_sound.loc[:, (slice(None), ['Top'], slice(None))])

        self._Z_Bottom_transmission_line = self.transform_Top2Bottom(char_impedance=self._Z0.loc[:, (slice(None), slice(None), ['Bottom'])].iloc[:, ::-1],
                                                                  length=self._transmission_line_length.loc[:, (slice(None), slice(None), ['Bottom'])].iloc[:, ::-1],
                                                                  frequency=self._frequency_band,
                                                                  sos=self._speed_of_sound.loc[:, (slice(None), slice(None), ['Bottom'])].iloc[:, ::-1])


        self._Z_impedance_acoustic_transmission_line = pd.DataFrame(np.column_stack((self._Z_Top_transmission_line,
                                                                                     self._Z_Bottom_transmission_line)),
                                                                    columns=['Top', 'Bottom'])



    # Convolve transmission through the individual acoustic layers
    #
    def transform_Top2Bottom(self, char_impedance=None, length=None, frequency=None, sos=None):

        # Retrieve number of necessary transformations
        #
        electrode_column_name = char_impedance.columns.get_level_values(0)[int(np.argwhere(char_impedance.columns.get_level_values(0).str.contains('electrode')))]
        electrode_idx_position = int(np.argwhere(char_impedance.columns.get_loc(electrode_column_name, method=None)))
        nbr_transformations = electrode_idx_position

        # Initilize arrays for transformation
        #
        Z0 = char_impedance.to_numpy()
        l = length.to_numpy()
        v = sos.to_numpy()
        Z_load = np.zeros((nbr_transformations, len(frequency))).astype(complex)

        for load_idx in range(nbr_transformations):
            transmission_line_idx = load_idx + 1
            if np.all(Z_load == Z_load[0]):
                Zin = Z0[:, 0]
            else:
                Zin = Z_load[load_idx - 1, :]

            Z_load[load_idx, :] = self.transmission_line(Z0=Z0[:, transmission_line_idx],
                                                         ZL=Zin,
                                                         beta=calculate_beta(frequency, v[:, transmission_line_idx]),
                                                         l=l[:, transmission_line_idx])

        return Z_load[load_idx]


    # CALCULATE TRANSMISSION LINE (Zin)
    #
    def transmission_line(self, Z0=None, ZL=None, beta=None, l=None):
        Zin = Z0 * (ZL + 1j * Z0 * np.tan(beta * l)) / (Z0 + 1j * ZL * np.tan(beta * l))
        return Zin


    @property
    def impedance(self):
        return self._Z_impedance_acoustic_transmission_line



class mason_piezo():
    def __init__(self, transducer=None, init=None, fband=None):

        self._v = float(transducer.material.loc['piezo', 'v'].values)
        self._t = float(transducer.geometry.loc['piezo', 'Thickness'].values)
        self._Z0 = float(init['piezo'].values)
        self._frequency_band = frequency_spectrum(fband)

        self._impedance_mason_piezo = pd.DataFrame(self.Tattenuator(),
                                                   columns=['Top', 'Center', 'Bottom'])


    # T-Network
    #
    # Z_Top = Z_Bottom = 1j * Z0 * tan(beta*t/2)
    # Z_Center = -1j * Z0 * 1/sin(beta*t)
    #
    def Tattenuator(self):
        Z_Top = Z_Bottom = 1j * self._Z0 * np.tan((calculate_beta(self._frequency_band, self._v) * self._t) / 2)
        Z_Center = -1j * self._Z0 / np.sin(calculate_beta(self._frequency_band, self._v) * self._t)
        return np.column_stack((Z_Top, Z_Center, Z_Bottom))


    @property
    def impedance(self):
        return self._impedance_mason_piezo



class mason_ac_transducer():
    def __init__(self, acoustic_struct=None, piezo=None):

        self._Z_acoustic_structure = acoustic_struct
        self._Z_piezo = piezo

        # Fuse Mason Impedance with Transmission Line Impedance
        #
        self._impedance_transducer_elements = self.serial_fuse_acoustic_circuit_impedance()


        # Fuse parallel impedance in Mason
        #
        self._impedance_parallel = parallel_circuit_impedance(self._impedance_transducer_elements['Top'].to_numpy(),
                                                              self._impedance_transducer_elements['Bottom'].to_numpy())


        # Fuse serial impedance in Mason
        #
        self._impedance_transducer = self._impedance_transducer_elements['Center'] + self._impedance_parallel


    def serial_fuse_acoustic_circuit_impedance(self):
        Z_structures = pd.concat([self._Z_piezo,
                              self._Z_acoustic_structure], axis=1)

        Z_transducer = pd.DataFrame(np.zeros_like(self._Z_piezo), columns=self._Z_piezo.columns)
        Z_transducer['Top'] = Z_structures[['Top']].sum(axis=1)
        Z_transducer['Bottom'] = Z_structures[['Bottom']].sum(axis=1)
        Z_transducer['Center'] = self._Z_piezo['Center']
        return Z_transducer



    @property
    def impedance(self):
        return self._impedance_transducer



class mason_transformer():
    def __init__(self, acoustic_struct=None, init=None):

        self._Z_acoustic_structure = acoustic_struct
        self._N = complex(init['N'].values)

        self._transfromed_impedance_ac2el = self.transform()

    # Transform acoustic impedance to electrical side
    #
    def transform(self):
        Z_transfromed_ac2el = self._Z_acoustic_structure * ((1 / self._N) ** 2)
        return Z_transfromed_ac2el

    @property
    def impedance(self):
        return self._transfromed_impedance_ac2el



class mason_el_transducer():
    def __init__(self, impedance=None, init=None, fband=None):

        self._Z_transformed = impedance
        self._C0 = complex(init['C0'].values)
        self._frequency_band = frequency_spectrum(fband)

        # Fuse the transformed impedance with negative serial capacitor impedance
        #
        self.serial_fuse_impedance = (-1 * self.capacitive_impedance()) + self._Z_transformed

        # Fuse the serial impedance with parallel capacitor impedance
        #
        self.parallel_fuse_impedance = parallel_circuit_impedance(self.capacitive_impedance(), self.serial_fuse_impedance)

        # Resulting electrical impedances
        #
        self.el_impedance_transducer = self.parallel_fuse_impedance

    def capacitive_impedance(self):
        Z_cap = (1 / (1j * 2 * np.pi * self._frequency_band * self._C0))
        return Z_cap

    @property
    def impedance(self):
        return self.el_impedance_transducer
