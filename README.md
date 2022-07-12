[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/luuleitner/xMason/blob/main/xmasonsim.ipynb)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

       

# xMason
This repository contains an adapted Mason model to calculate impedance responses of printed ultrasonic transducers. 

## Model details
For the simulation of the electro-acoustic behaviour of transducers we use a simulation model based on the transducer circuit proposed by Mason*. Mason suggested a circuit of lumped elements as a replica to describe the electro-mechanical behaviour of a piezoelectric element. 

<p align="center">
<img src="https://github.com/luuleitner/xMason/blob/main/data/MasonModel.jpg" height="400">
</p>
Mason model characteristics:

- acoustic transmission line of the transducer is replaced by an equivalent electric T-network (see figure above central part). 
- Mason's transformer converts electrical impedance's into acoustical and vice versa. 
- an electrical interface consisting of two in-parallel connected capacitors with inverted capacitance and a terminal for in- and output voltages. 

The main difference between our simulation model and the original circuit proposed by Mason are additional lossless acoustic transmission lines at the top and bottom of the transducer representing: air (blue), electrodes (dark grey), substrate (brown). Using transmission line theory, the impedance loads imposed by further acoustic structures are propagated towards the piezoelectric element where they act as input loads for the T-net. Thus, the acoustic behaviour of substructures, for example, air, electrodes, substrates can be considered in the simulation. 

A frequency band [f{low}, f_{high}] is used to calculate the resulting electrical impedance, i.e. the impedance seen at the electrical connection across capacitor C_0. 


**W. P. Mason, Electromechanical Transducers and Wave Filters, 1st ed. New York: D. van Nostrand Company Inc., 1942.*

## Usage
This repository contains the python source code of `xMason` as well as the data set published in the 2022 IEEE ISAF conference recorded with a vector network analyser on 6 printed PVDF transducers. A browser based online service for claculations is available via [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/luuleitner/xMason/blob/main/xmasonsim.ipynb)

## <a name="citation_1"></a> Publications
```
[1] @inproceedings{c:leitner2022,
      title={Design Automation for a Fully Printed P(VDF-TrFE) Transducer},
      year={2022}  
      author={Leitner, Christoph and Keller, Kirill and Thurner, Stephan and Baumgartner, Christian and Greco, Francesco and Scharfetter, Hermann and Schröttner, Jörg},
      journal = {2022 IEEE International Symposium on Applications of Ferroelectrics (ISAF)},
      publisher={IEEE},
      }
```
    
# License

This program is free software and licensed under the Apache License v2.0 - see the [LICENSE](https://github.com/luuleitner/xMason/blob/main/LICENSE) file for details.
