# ![Open Quantum Design](docs/img/oqd-logo-text.png)
![Python](https://img.shields.io/badge/Python-3.11-blue)

<h2 align="center">
    Open Quantum Design: Cloud
</h2>

## What's Here
This repository contains the software needed to submit jobs to a remote, cloud server for classical simulations of quantum programs.
In addition, it provides a Docker script to self-host a simulation server of the OQD emulator backends.

## Installation
To install locally for development or launching a Docker container server:

```bash
git clone https://github.com/OpenQuantumDesign/oqd-cloud.git
pip install .
```

To start the simulation server, ensure Docker is installed on the machine, navigate to the `docker` folder, and run,
```bash
docker compose up
```

To serve the documentation, 
```bash
pip install .[docs]
mkdocs serve
```
