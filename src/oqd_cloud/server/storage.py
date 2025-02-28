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

from typing import Literal
from minio import Minio
import os

from fastapi import APIRouter, HTTPException
from fastapi import status as http_status

########################################################################################
import oqd_analog_emulator #.qutip_backend import QutipBackend
import oqd_trical
from oqd_core.backend.task import Task
from rq.job import Callback
from rq.job import Job as RQJob
from sqlalchemy import select

from oqd_cloud.server.database import JobInDB, db_dependency
from oqd_cloud.server.model import Job, Backends
from oqd_cloud.server.route.auth import user_dependency

########################################################################################

minio_client = Minio(
    "127.0.0.1:9000",
    access_key="admin",
    secret_key="password",
    secure=False
)

# %%
source_file = "./tests/atomic.json"
bucket_name = "oqd-cloud-bucket"
destination_file = "my-test-file.txt"

minio_client.fput_object(
    bucket_name, destination_file, source_file,
)