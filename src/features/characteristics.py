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

        # h33 = k * sqrt(c33/eps33)
        #
        # self._h33 = complex(self._transducer_material.loc[(['piezo'], slice(None), slice(None)), 'k'].values) * \
        #             np.sqrt(complex(self._transducer_material.loc[(['piezo'], slice(None), slice(None)), 'c33'].values) /
        #                     complex(self._transducer_material.loc[(['piezo'], slice(None), slice(None)), 'eps33'].values))
        self._h33 = complex(self._transducer_material.loc[(['piezo'], slice(None), slice(None)), 'h33'].values)

        self._init_electric_circuit = self.Eport()
        self._init_acoustic_circuit = self.Aport()



    # Characteristic Properties of capacitor and transformer
    # C0 (static capacitance) = epsT33 (dielectric constant in thickness) * A (area) / t (thickness of piezo)
    # N (transformer voltage ratio) = C0 (static capacitance) * h33 (piezoelectric constant in thickness)
    #
    # Piezoelectric constant: https://piezo.com/pages/piezo-terminology-glossary#:~:text=The%20piezoelectric%20constants%20relating%20the%20electric%20field%20produced%20by%20a,meter%20per%20newtons%2Fsquare%20meter.
    def Eport(self):
        C0 = self._e33 * ((self._transducer_geometry.loc[(['piezo'], slice(None), slice(None)), 'Diameter'] ** 2) * np.pi / 4) \
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
                                      diameter=float(self._transducer_geometry.loc[(['Telectrode'], slice(None), slice(None)), 'Diameter'].values))

        Z0_Bload = acoustic_impedance(density=float(self._transducer_material.loc[(['Tload'], slice(None), slice(None)), 'roh'].values),
                                      sos=float(self._transducer_material.loc[(['Tload'], slice(None), slice(None)), 'v'].values),
                                      shape='circular',
                                      diameter=float(self._transducer_geometry.loc[(['Telectrode'], slice(None), slice(None)), 'Diameter'].values))


        # Electrode Layers
        #
        Z0_Tel = acoustic_impedance(density=float(self._transducer_material.loc[(['Telectrode'], slice(None), slice(None)), 'roh'].values),
                                    sos=float(self._transducer_material.loc[(['Telectrode'], slice(None), slice(None)), 'v'].values),
                                    shape='circular',
                                    diameter=float(self._transducer_geometry.loc[(['Telectrode'], slice(None), slice(None)), 'Diameter'].values))

        Z0_Bel = acoustic_impedance(density=float(self._transducer_material.loc[(['Telectrode'], slice(None), slice(None)), 'roh'].values),
                                    sos=float(self._transducer_material.loc[(['Telectrode'], slice(None), slice(None)), 'v'].values),
                                    shape='circular',
                                    diameter=float(self._transducer_geometry.loc[(['Telectrode'], slice(None), slice(None)), 'Diameter'].values))


        # Transducer Layer
        #
        Z0_piezo = acoustic_impedance(density=float(self._transducer_material.loc[(['piezo'], slice(None), slice(None)), 'roh'].values),
                                      sos=float(self._transducer_material.loc[(['piezo'], slice(None), slice(None)), 'v'].values),
                                      shape='circular',
                                      diameter=float(self._transducer_geometry.loc[(['piezo'], slice(None), slice(None)), 'Diameter'].values))


        # Substrate Layer (Backing)
        #
        if ~np.isnan(self._transducer_geometry.loc[(['Bsubstrate'], slice(None), slice(None)), 'Diameter'].values):
            Z0_substrate = acoustic_impedance(density=float(self._transducer_material.loc[(['Bsubstrate'], slice(None), slice(None)), 'roh'].values),
                                              sos=float(self._transducer_material.loc[(['Bsubstrate'], slice(None), slice(None)), 'v'].values),
                                              shape='circular',
                                              diameter=float(self._transducer_geometry.loc[(['Bsubstrate'], slice(None), slice(None)), 'Diameter'].values))
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
        circular_area = ((kwargs.pop('diameter') ** 2) * np.pi) / 4
        return ((density * sos) * circular_area)
    if shape == 'rectangular':
        rectangular_area = (kwargs.pop('width') * kwargs.pop('height'))
        return ((density * sos) * rectangular_area)
    else:
        return (density * sos)
