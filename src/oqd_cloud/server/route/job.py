# Copyright 2024 Open Quantum Design

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

from fastapi import APIRouter, HTTPException
from fastapi import status as http_status

from rq.job import Callback
from rq.job import Job as RQJob

from sqlalchemy import select

########################################################################################

from oqd_analog_emulator.qutip_backend import QutipBackend

from oqd_core.interface.analog import *
from oqd_core.backend.task import Task

from oqd_cloud.server.route.auth import user_dependency
from oqd_cloud.server.database import db_dependency, JobInDB
from oqd_cloud.server.jobqueue import (
    redis_client,
    queue,
    report_success,
    report_failure,
    report_stopped,
)
from oqd_cloud.server.model import Job

########################################################################################

job_router = APIRouter(tags=["Job"])


@job_router.post("/submit/{backend}", tags=["Job"])
async def submit_job(
    task: Task,
    backend: Literal["analog-qutip",],
    user: user_dependency,
    db: db_dependency,
):
    print(task)
    print(f"Queueing {task} on server {backend} backend. {len(queue)} jobs in queue.")

    backends = {
        "analog-qutip": QutipBackend(),
        # "tensorcircuit": TensorCircuitBackend()
    }
    # backends_run = {
    #     "analog-qutip": lambda task: backends["analog-qutip"].run(task=task)
    # }

    if backend == "analog-qutip":
        try:
            expt, args = backends[backend].compile(task=task)
        except Exception as e:
            raise Exception("Cannot properly compile to the QutipBackend.")

    job = queue.enqueue(
        backends[backend].run,
        task,
        on_success=Callback(report_success),
        on_failure=Callback(report_failure),
        on_stopped=Callback(report_stopped),
    )

    job_in_db = JobInDB(
        job_id=job.id,
        task=task.model_dump_json(),
        backend=backend,
        status=job.get_status(),
        result=None,
        user_id=user.user_id,
    )
    db.add(job_in_db)
    await db.commit()
    await db.refresh(job_in_db)

    return Job.model_validate(job_in_db)


@job_router.get("/retrieve/{job_id}", tags=["Job"])
async def retrieve_job(job_id: str, user: user_dependency, db: db_dependency):
    query = await db.execute(
        select(JobInDB).filter(
            JobInDB.job_id == job_id,
            JobInDB.user_id == user.user_id,
        )
    )
    job_in_db = query.scalars().first()
    if job_in_db:
        return Job.model_validate(job_in_db)

    raise HTTPException(status_code=http_status.HTTP_401_UNAUTHORIZED)


@job_router.delete("/cancel/{job_id}", tags=["Job"])
async def cancel_job(job_id: str, user: user_dependency, db: db_dependency):
    query = await db.execute(
        select(JobInDB).filter(
            JobInDB.job_id == job_id,
            JobInDB.user_id == user.user_id,
        )
    )
    job_in_db = query.scalars().first()
    if job_in_db:
        job = RQJob.fetch(id=job_id, connection=redis_client)
        job.cancel()
        setattr(job_in_db, "status", "canceled")
        await db.commit()
        await db.refresh(job_in_db)
        return Job.model_validate(job_in_db)

    raise HTTPException(status_code=http_status.HTTP_401_UNAUTHORIZED)
