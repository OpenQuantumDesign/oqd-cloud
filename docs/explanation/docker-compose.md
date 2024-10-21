## Emulation Server - Docker Compose
The Docker compose script (`docker/docker-compose.yaml`) runs a backend emulation server. 
Once initialized, users can run jobs on the cloud server to emulate any quantum program, expressed as 
an `AnalogCircuit`, `DigitalCircuit`, or `AtomicCircuit`, on the supported the backend emulators.
Currently, the `Analog` layer `QutipBackend` is supported. 

The server uses Redis to queue submitted jobs and a PostgreSQL database for storing and retrieving 
users and jobs.

To initialize the server, install Docker following 
the [installation instructions](https://docs.docker.com/engine/install/).
Then, it should be as simple as navigating to the `docker/` path,
```bash 
cd /docker/
```
and running,
```bash 
docker compose up
```
If all services are initialized and correctly, the outputs should be displayed in the terminal. 
To run in the background, use the `--detach` or `-d` flag:
```bash
docker compose up -d
```
