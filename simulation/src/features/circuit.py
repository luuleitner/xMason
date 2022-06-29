from datetime import datetime
from MASONmodel.src.features.characteristics import Model_init
from MASONmodel.src.features.ports import acoustic_transmission_line
from MASONmodel.src.features.ports import mason_piezo, mason_ac_transducer, mason_transformer, mason_el_transducer

class Transducer_acoustic_circuit():
    def __init__(self, transducer=None, fband=None):

        print('Initializing model... ')
        start_time = datetime.now()
        #
        self._characteristic_impedance = Model_init(transducer=transducer).Z0_acoustic
        self._el_element_characteristic = Model_init(transducer=transducer).electric
        #
        end_time = datetime.now()
        init_time = end_time - start_time
        print('')
        print(f'Model initialized in {init_time.total_seconds()} seconds')



        print('')
        print('Start simulation... ')
        start_time = datetime.now()
        #
        self._impedance_acoustic_structures = acoustic_transmission_line(transducer=transducer,
                                                                         init=self._characteristic_impedance,
                                                                         fband=fband).impedance

        self._impedance_mason_piezo = mason_piezo(transducer=transducer,
                                                  init=self._characteristic_impedance,
                                                  fband=fband).impedance

        self._impedance_ac_transducer = mason_ac_transducer(acoustic_struct=self._impedance_acoustic_structures,
                                                            piezo=self._impedance_mason_piezo).impedance

        self._impedance_transformer = mason_transformer(acoustic_struct=self._impedance_ac_transducer,
                                                        init=self._el_element_characteristic).impedance

        self._impedance_el_transducer = mason_el_transducer(impedance=self._impedance_transformer,
                                                            init=self._el_element_characteristic,
                                                            fband=fband).impedance
        #
        end_time = datetime.now()
        init_time = end_time - start_time
        print('')
        print(f'Impedance simulation took {init_time.total_seconds()}seconds')



    @property
    def electric_impedance(self):
        return self._impedance_el_transducer


