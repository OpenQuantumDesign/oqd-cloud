# ![Open Quantum Design](https://raw.githubusercontent.com/OpenQuantumDesign/oqd-compiler-infrastructure/main/docs/img/oqd-logo-text.png)

<h2 align="center">
    Open Quantum Design: Cloud
</h2>

[![docs](https://img.shields.io/badge/documentation-lightblue)](https://docs.openquantumdesign.org/open-quantum-design-cloud)
[![PyPI Version](https://img.shields.io/pypi/v/oqd-cloud)](https://pypi.org/project/oqd-cloud)
[![CI](https://github.com/OpenQuantumDesign/oqd-cloud/actions/workflows/pytest.yml/badge.svg)](https://github.com/OpenQuantumDesign/oqd-cloud/actions/workflows/pytest.yml)
![versions](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue)
[![License: Apache 2.0](https://img.shields.io/badge/license-Apache%202.0-brightgreen.svg)](https://opensource.org/licenses/Apache-2.0)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)



## What's Here
This repository contains the software needed to submit jobs to a remote, cloud server for classical simulations of quantum programs.
In addition, it provides a Docker script to self-host a simulation server of the OQD emulator backends.

## Installation
```bash 
pip install oqd-cloud
```

To install locally for development or launching a Docker container server:

```bash
git clone https://github.com/OpenQuantumDesign/oqd-cloud.git
pip install .
```

To start the simulation server, ensure Docker is installed on the machine, navigate to the `docker` folder, and run,
```bash
cd oqd-cloud/docker
docker compose up -d
```

To serve the documentation, 
```bash
pip install .[docs]
mkdocs serve
```

### Where in the stack
```mermaid
block-beta
   columns 3

   block:Interface
       columns 1
       InterfaceTitle("<i><b>Interfaces</b><i/>")
       InterfaceDigital["<b>Digital Interface</b>\nQuantum circuits with discrete gates"]
       space
       InterfaceAnalog["<b>Analog Interface</b>\n Continuous-time evolution with Hamiltonians"]
       space
       InterfaceAtomic["<b>Atomic Interface</b>\nLight-matter interactions between lasers and ions"]
       space
    end

    block:IR
       columns 1
       IRTitle("<i><b>IRs</b><i/>")
       IRDigital["Quantum circuit IR\nopenQASM, LLVM+QIR"]
       space
       IRAnalog["openQSIM"]
       space
       IRAtomic["openAPL"]
       space
    end

    block:Emulator
       columns 1
       EmulatorsTitle("<i><b>Classical Emulators</b><i/>")

       EmulatorDigital["Pennylane, Qiskit"]
       space
       EmulatorAnalog["QuTiP, QuantumOptics.jl"]
       space
       EmulatorAtomic["TrICal, QuantumIon.jl"]
       space
    end

    space
    block:RealTime
       columns 1
       RealTimeTitle("<i><b>Real-Time</b><i/>")
       space
       RTSoftware["ARTIQ, DAX, OQDAX"]
       space
       RTGateware["Sinara Real-Time Control"]
       space
       RTHardware["Lasers, Modulators, Photodetection, Ion Trap"]
       space
       RTApparatus["Trapped-Ion QPU (<sup>171</sup>Yb<sup>+</sup>, <sup>133</sup>Ba<sup>+</sup>)"]
       space
    end
    space

   InterfaceDigital --> IRDigital
   InterfaceAnalog --> IRAnalog
   InterfaceAtomic --> IRAtomic

   IRDigital --> IRAnalog
   IRAnalog --> IRAtomic

   IRDigital --> EmulatorDigital
   IRAnalog --> EmulatorAnalog
   IRAtomic --> EmulatorAtomic

   IRAtomic --> RealTimeTitle

   RTSoftware --> RTGateware
   RTGateware --> RTHardware
   RTHardware --> RTApparatus

   classDef title fill:#23627D,stroke:#141414,color:#FFFFFF;
   classDef digital fill:#c3e1ee,stroke:#141414,color:#141414;
   classDef analog fill:#afd7e9,stroke:#141414,color:#141414;
   classDef atomic fill:#9ccee3,stroke:#141414,color:#141414;
   classDef realtime fill:#88c4dd,stroke:#141414,color:#141414;

    classDef highlight fill:#F19D19,stroke:#141414,color:#141414,stroke-dasharray: 5 5;
    classDef normal fill:#fcebcf,stroke:#141414,color:#141414;

    class InterfaceTitle,IRTitle,EmulatorsTitle,RealTimeTitle title
    class InterfaceDigital,IRDigital,EmulatorDigital digital
    class InterfaceAnalog,IRAnalog,EmulatorAnalog analog
    class InterfaceAtomic,IRAtomic,EmulatorAtomic atomic
    class RTSoftware,RTGateware,RTHardware,RTApparatus realtime

   class Emulator highlight

   class Interface normal
   class RealTime normal
   class IR normal
    
```
The tools in this repository allow for self-hosting a server to run
quantum programs on classical emulators, highlighted in the stack diagram in red. 
A client can specify a quantum program, submit it as a job to the self-hosted server,
and retrieve the emulation results.

Currently, the analog layer backend is supported.