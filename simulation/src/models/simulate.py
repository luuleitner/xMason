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

from simulation.src.data.loader import Material
from simulation.src.features.transducer import Transducer
from simulation.src.features.circuit import Transducer_acoustic_circuit


class simulate_xMason():
    def __init__(self, parameters=None, matpath=None):

        # Material Path
        self.matpath = matpath

        # Frequency Band
        self._fband = parameters['fband']

        # Geometries
        self._radius = parameters['radius']
        if 'substrateWHratio' in parameters:
            self._substrateWHratio = parameters['substrateWHratio']
        else:
            self._substrateWHratio = None
        self._thickness_td= parameters['thickness_td']
        self._thickness_el = parameters['thickness_el']
        self._thickness_sub = parameters['thickness_sub']

        # Materials
        self._Tload = parameters['Tload']
        self._Telectrode = parameters['Telectrode']
        self._piezo = parameters['piezo']
        self._Belectrode = parameters['Belectrode']
        self._Bsubstrate = parameters['Bsubstrate']
        self._Bload = parameters['Bload']



        ################################################################
        # LOAD MATERIALS --------->
        ################################################################
        MatData = Material(self.matpath)


        ################################################################
        # Initialize TRANSDUCER --------->
        ################################################################
        #
        # Define Materials using following *kwargs:
        # Tload, Telectrode, piezo, Belectrode, Bsubstrate, Bload
        # T = Top orientation
        # B = Bottom orientation
        #
        xMason_Transducer = Transducer(radius=self._radius,
                                       substrateWHratio=self._substrateWHratio,
                                       thickness_td=self._thickness_td,
                                       thickness_el=self._thickness_el,
                                       thickness_sub=self._thickness_sub,
                                       material=MatData.material,
                                       Tload=self._Tload,
                                       Telectrode=self._Telectrode,
                                       piezo=self._piezo,
                                       Belectrode=self._Belectrode,
                                       Bsubstrate=self._Bsubstrate,
                                       Bload=self._Bload)

        ################################################################
        # Simulate IMPEDANCE for defined frequency band --------->
        ################################################################
        self._xMason_Simulation = Transducer_acoustic_circuit(transducer=xMason_Transducer,
                                                             fband=self._fband)


    @property
    def impedance(self):
        return self._xMason_Simulation
