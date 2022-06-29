"""
   Copyright (C) 2022 Graz University of Technology. All rights reserved.

   Author: Christoph Leitner, Graz University of Technology

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

import os
from pathlib import Path

from src.data.loader import Material
from src.features.transducer import Transducer
from src.features.circuit import Transducer_acoustic_circuit


class simulate_xMason():
    def __init__(self, parameters=None):

        # Frequency Band
        self._fband = parameters['fband']

        # Geometries
        self._diameter = parameters['diameter']
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
        python_project_path = str(Path(os.getcwd()).parents[0])
        ARG_MATERIAL_PATH = os.path.join(python_project_path, 'MASONmodel\data\materials.csv')
        MatData = Material(ARG_MATERIAL_PATH)


        ################################################################
        # Initialize TRANSDUCER --------->
        ################################################################
        #
        # Define Materials using following *kwargs:
        # Tload, Telectrode, piezo, Belectrode, Bsubstrate, Bload
        # T = Top orientation
        # B = Bottom orientation
        #
        xMason_Transducer = Transducer(diameter=self._diameter,
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
