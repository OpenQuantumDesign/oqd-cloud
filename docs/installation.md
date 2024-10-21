
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
