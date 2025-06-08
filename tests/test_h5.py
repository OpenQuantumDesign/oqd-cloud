# %%
from h5pydantic import H5Dataset, H5Group, H5Int64


class Baseline(H5Group):
    temperature: float
    humidity: float


class Metadata(H5Group):
    start: Baseline
    end: Baseline


class Acquisition(H5Dataset, shape=(3, 5), dtype=H5Int64):
    beamstop: H5Int64


class Experiment(H5Group):
    metadata: Metadata
    data: list[Acquisition] = []


# %%
# from model import Experiment, Acquisition, Baseline, Metadata

import numpy as np
from pathlib import Path
from rich.pretty import pprint

experiment = Experiment(
    data=[Acquisition(beamstop=11), Acquisition(beamstop=12)],
    metadata=Metadata(
        start=Baseline(temperature=25.0, humidity=0.4),
        end=Baseline(temperature=26.0, humidity=0.4),
    ),
)

with experiment.dump(Path("experiment.hdf")):
    experiment.data[0][()] = np.random.randint(255, size=(3, 5))
    experiment.data[1][()] = np.random.randint(255, size=(3, 5))

pprint(experiment)

# %%
experiment



# %%
