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


class Model_init():
    #
    # Arshed A.M. et al 2014, "Influence of a silver epoxy dopant on the
    # performance of broken piezoelectric ceramic transducer based on an analytical model",
    # Smart Mater. Struct., 23, 045036.
    #
    def __init__(self, transducer=None):
        self._transducer_geometry = transducer.geometry
        self._transducer_material = transducer.material

        self._e33 = complex(self._transducer_material.loc[(['piezo'], slice(None), slice(None)), 'eps33'].values)
        self._h33 = complex(self._transducer_material.loc[(['piezo'], slice(None), slice(None)), 'h33'].values)

        self._init_electric_circuit = self.Eport()
        self._init_acoustic_circuit = self.Aport()



    # Characteristic Properties of capacitor and transformer
    # C0 (static capacitance) = epsT33 (dielectric constant in thickness) * A (area) / t (thickness of piezo)
    # N (transformer voltage ratio) = C0 (static capacitance) * h33 (piezoelectric constant in thickness)
    #
    # Piezoelectric constant: https://piezo.com/pages/piezo-terminology-glossary#:~:text=The%20piezoelectric%20constants%20relating%20the%20electric%20field%20produced%20by%20a,meter%20per%20newtons%2Fsquare%20meter.
    def Eport(self):
        C0 = self._e33 * ((self._transducer_geometry.loc[(['piezo'], slice(None), slice(None)), 'Radius'] ** 2) * np.pi / 4) \
             / self._transducer_geometry.loc[(['piezo'], slice(None), slice(None)), 'Thickness']
        N = C0 * self._h33
        return pd.DataFrame([C0, N], index=['C0', 'N']).T



    # Characteristic Impedance for Acoustic Elements
    # Z0 = [roh (density) * v (propagation velocity)] / A (area)
    #
    #
    def Aport(self):

        # Acoustic Loads
        #
        Z0_Tload = acoustic_impedance(density=float(self._transducer_material.loc[(['Tload'], slice(None), slice(None)), 'roh'].values),
                                      sos=float(self._transducer_material.loc[(['Tload'], slice(None), slice(None)), 'v'].values),
                                      shape='circular',
                                      radius=float(self._transducer_geometry.loc[(['Telectrode'], slice(None), slice(None)), 'Radius'].values))

        Z0_Bload = acoustic_impedance(density=float(self._transducer_material.loc[(['Tload'], slice(None), slice(None)), 'roh'].values),
                                      sos=float(self._transducer_material.loc[(['Tload'], slice(None), slice(None)), 'v'].values),
                                      shape='circular',
                                      radius=float(self._transducer_geometry.loc[(['Telectrode'], slice(None), slice(None)), 'Radius'].values))


        # Electrode Layers
        #
        Z0_Tel = acoustic_impedance(density=float(self._transducer_material.loc[(['Telectrode'], slice(None), slice(None)), 'roh'].values),
                                    sos=float(self._transducer_material.loc[(['Telectrode'], slice(None), slice(None)), 'v'].values),
                                    shape='circular',
                                    radius=float(self._transducer_geometry.loc[(['Telectrode'], slice(None), slice(None)), 'Radius'].values))

        Z0_Bel = acoustic_impedance(density=float(self._transducer_material.loc[(['Telectrode'], slice(None), slice(None)), 'roh'].values),
                                    sos=float(self._transducer_material.loc[(['Telectrode'], slice(None), slice(None)), 'v'].values),
                                    shape='circular',
                                    radius=float(self._transducer_geometry.loc[(['Telectrode'], slice(None), slice(None)), 'Radius'].values))


        # Transducer Layer
        #
        Z0_piezo = acoustic_impedance(density=float(self._transducer_material.loc[(['piezo'], slice(None), slice(None)), 'roh'].values),
                                      sos=float(self._transducer_material.loc[(['piezo'], slice(None), slice(None)), 'v'].values),
                                      shape='circular',
                                      radius=float(self._transducer_geometry.loc[(['piezo'], slice(None), slice(None)), 'Radius'].values))


        # Substrate Layer (Backing)
        #
        if ~np.isnan(self._transducer_geometry.loc[(['Bsubstrate'], slice(None), slice(None)), 'Radius'].values):
            Z0_substrate = acoustic_impedance(density=float(self._transducer_material.loc[(['Bsubstrate'], slice(None), slice(None)), 'roh'].values),
                                              sos=float(self._transducer_material.loc[(['Bsubstrate'], slice(None), slice(None)), 'v'].values),
                                              shape='circular',
                                              radius=float(self._transducer_geometry.loc[(['Bsubstrate'], slice(None), slice(None)), 'Radius'].values))
        else:
            Z0_substrate = acoustic_impedance(density=float(self._transducer_material.loc[(['Bsubstrate'], slice(None), slice(None)), 'roh'].values),
                                              sos=float(self._transducer_material.loc[(['Bsubstrate'], slice(None), slice(None)), 'v'].values),
                                              shape='rectangular',
                                              height=float(self._transducer_geometry.loc[(['Bsubstrate'], slice(None), slice(None)), 'Width'].values),
                                              width=float(self._transducer_geometry.loc[(['Bsubstrate'], slice(None), slice(None)), 'Height'].values))


        # Set all elements together in a pandas array
        Z0 = pd.DataFrame([Z0_Tload,
                           Z0_Tel,
                           Z0_piezo,
                           Z0_Bel,
                           Z0_substrate,
                           Z0_Bload],
                          index=self._transducer_material.index.to_list())

        midx = pd.MultiIndex.from_tuples(Z0.index.to_list())
        Z0 = Z0.reset_index(drop=True).set_index(midx).T

        return Z0.fillna(0)


    @property
    def Z0_acoustic(self):
        return self._init_acoustic_circuit

    @property
    def electric(self):
        return self._init_electric_circuit



def acoustic_impedance(density=None, sos=None, shape=None, **kwargs):
    if shape == 'circular':
        circular_area = ((kwargs.pop('radius') ** 2) * np.pi) / 4
        return ((density * sos) * circular_area)
    if shape == 'rectangular':
        rectangular_area = (kwargs.pop('width') * kwargs.pop('height'))
        return ((density * sos) * rectangular_area)
    else:
        return (density * sos)
