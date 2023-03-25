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


import numpy as np
import pandas as pd

class Transducer():
    def __init__(self,
                 radius=None,
                 substrateWHratio=None,
                 thickness_td=None,
                 thickness_tel=None,
                 thickness_bel=None,
                 thickness_sub=None,
                 material=None,
                 **kwargs):

######### Create a layer stack list of the full circuit model transducer
        #
        self._stack_index = self.__stack_indexing(layers=list(kwargs))
        self._transducer_stack = self.__stack_layers(layers=list(kwargs))
        self._transducer_stack = self.__transducer_indexing(self._transducer_stack)


######### Create pandas array with the geometry of transducer elements
        #
        geometry_cols = ['Radius', 'Width', 'Height', 'Thickness']
        self._geometry = pd.DataFrame(np.zeros((len(self._stack_index[0]), len(geometry_cols))),
                                      index=self._stack_index,
                                      columns=geometry_cols)
        if substrateWHratio:
            self._geometry.loc[['Tload', 'Telectrode', 'piezo', 'Belectrode', 'Bload'], 'Radius'] = radius
            self._geometry.loc[['Bsubstrate'], 'Width'] = substrateWHratio[0]
            self._geometry.loc[['Bsubstrate'], 'Height'] = substrateWHratio[1]
        else:
            self._geometry.loc[['Tload', 'Telectrode', 'piezo', 'Belectrode', 'Bsubstrate', 'Bload'], 'Radius'] = radius


        self._geometry.loc[:, 'Thickness'] = [np.nan,
                                          thickness_tel,
                                          thickness_td,
                                          thickness_bel,
                                          thickness_sub,
                                          np.nan]
        self._geometry.replace(0, np.nan, inplace=True)


######### Create a pandas array with the materials of transducer elements
        #
        self._material = material
        self._Tload = self._material.loc[(self._material == kwargs.pop('Tload')).any(axis=1)]
        self._Telectrode = self._material.loc[(self._material == kwargs.pop('Telectrode')).any(axis=1)]
        self._piezo = self._material.loc[(self._material == kwargs.pop('piezo')).any(axis=1)]
        self._Belectrode = self._material.loc[(self._material == kwargs.pop('Belectrode')).any(axis=1)]
        self._Bsubstrate = self._material.loc[(self._material == kwargs.pop('Bsubstrate')).any(axis=1)]
        self._Bload = self._material.loc[(self._material == kwargs.pop('Bload')).any(axis=1)]

        if kwargs.__len__() != 0:
            print(f'ERROR: Wrong keyword for transducer structure encountered.')
            print(f'{kwargs} are not valid inputs.')
            print('Stopping execution')
            exit()


        self._transducer = pd.concat([self._Tload,
                                      self._Telectrode,
                                      self._piezo,
                                      self._Belectrode,
                                      self._Bsubstrate,
                                      self._Tload]).reset_index(drop=True)
        midx = pd.MultiIndex.from_arrays(self._stack_index)
        self._transducer = self._transducer.set_index(midx)

        self._transducer = self._transducer.drop(['Details', 'Source', 'Material'], level=0, axis=1)



    def __stack_indexing(self, layers=None):
        stack = layers
        Tindex = np.empty_like(stack)
        Bindex = np.empty_like(stack)
        Tindex[:stack.index('piezo')+1] = 'Top'
        Bindex[stack.index('piezo'):] = 'Bottom'

        return [stack, Tindex.tolist(), Bindex.tolist()]


    def __stack_layers(self, layers=None):
        stack = layers
        stack[stack.index('piezo')] = 'Bpiezo'
        stack.insert(stack.index('Bpiezo'), 'Tpiezo')
        # stack = ['TacPort'] + stack + ['BacPort']
        return stack


    def __transducer_indexing(self, layers=None):
        stack = layers
        Tindex = np.empty_like(stack)
        Bindex = np.empty_like(stack)
        Tindex[:stack.index('Bpiezo')] = 'Top'
        Bindex[stack.index('Bpiezo'):] = 'Bottom'

        return [stack, Tindex.tolist(), Bindex.tolist()]


    @property
    def geometry(self):
        return self._geometry

    @property
    def material(self):
        return self._transducer

    @property
    def stack(self):
        return self._transducer_stack

    @property
    def midx_stack(self):
        return self._stack_index


