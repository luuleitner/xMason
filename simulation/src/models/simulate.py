import os
from pathlib import Path

from simulation.src.data.loader import Material
from simulation.src.features.transducer import Transducer
from simulation.src.features.circuit import Transducer_acoustic_circuit


class simulate_xMason():
    def __init__(self, parameters=None):

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
