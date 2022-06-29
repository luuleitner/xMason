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

import setuptools
from setuptools import setup, find_packages

setup(
    name='xMason',
    version='1.0',
    packages=setuptools.find_packages(),
    url='https://github.com/luuleitner/xMason',
    license='Apache-2.0',
    author='Christoph Leitner',
    description='Design Automation for a Fully Printed P(VDF-TrFE) Transducer',
    install_requires = ['tqdm', 'numpy', 'matplotlib', 'pandas'],
)