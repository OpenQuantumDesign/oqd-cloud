# Copyright 2024-2025 Open Quantum Design

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


# %%
# import matplotlib.pyplot as plt
# import numpy as np
# import seaborn as sns
# from oqd_analog_emulator.qutip_backend import QutipBackend
from oqd_core.backend.metric import Expectation
from oqd_core.backend.task import Task, TaskArgsAnalog
from oqd_core.interface.analog.operation import AnalogCircuit, AnalogGate
from oqd_core.interface.analog.operator import PauliX, PauliZ

from oqd_core.interface.atomic.circuit import AtomicCircuit

from oqd_cloud.client import Client
from oqd_cloud.provider import Provider
from rich.pretty import pprint 

X = PauliX()
Z = PauliZ()

Z.model_validate_json(Z.model_dump_json())

Hx = AnalogGate(hamiltonian=(2 * X + Z))

op = 2 * X + Z
print(op.model_dump_json())


print(Hx)
print(Hx.model_dump_json())
print(AnalogGate.model_validate_json(Hx.model_dump_json()))

circuit = AnalogCircuit()
circuit.evolve(duration=10, gate=Hx)

print(circuit)
print(circuit.model_dump_json())
print(AnalogCircuit.model_validate_json(circuit.model_dump_json()))

circuit.model_json_schema()

# define task args
args = TaskArgsAnalog(
    n_shots=100,
    fock_cutoff=4,
    metrics={
        "Z": Expectation(operator=Z),
    },
    dt=1e-3,
)

task = Task(program=circuit, args=args)
task.model_dump_json()


#%%
client = Client()
provider = Provider(port=8007)
client.connect(provider=provider, username="ben", password="pwd")
client.status_report

#%%
backends = provider.available_backends
print(backends)

# %%
print(client.jobs)
job = client.submit_job(task=task, backend="oqd-analog-emulator-qutip", tags='a')
pprint(job)

# %%
client.retrieve_job(job_id=job.job_id)
