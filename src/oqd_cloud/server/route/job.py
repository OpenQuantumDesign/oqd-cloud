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

from typing import Literal, Annotated

from fastapi import APIRouter, HTTPException, Body
from fastapi import status as http_status

########################################################################################
import oqd_analog_emulator  # .qutip_backend import QutipBackend
import oqd_trical
from oqd_core.backend.task import Task
from rq.job import Callback
from rq.job import Job as RQJob
from sqlalchemy import select

from oqd_cloud.server.database import JobInDB, db_dependency
from oqd_cloud.server.jobqueue import (
    queue,
    redis_client,
    report_failure,
    report_stopped,
    report_success,
)
from oqd_cloud.server.model import Job, Backends
from oqd_cloud.server.route.auth import user_dependency

########################################################################################

_backends = {
    "oqd-analog-emulator-qutip": oqd_analog_emulator.qutip_backend.QutipBackend(),
    "oqd-trical-qutip": oqd_trical.backend.qutip.QutipBackend(),
    "oqd-trical-dynamiqs": oqd_trical.backend.dynamiqs.DynamiqsBackend(),
}
backends = Backends(available=list(_backends.keys()))

job_router = APIRouter(tags=["Job"])


@job_router.get("/available_backends")
async def available_backends():
    return backends


@job_router.post("/submit/{backend}", tags=["Job"])
async def submit_job(
    backend: Literal[tuple(backends.available)],
    task: Task,
    tags: Annotated[str, Body()],
    user: user_dependency,
    db: db_dependency,
):
    print(f"Queueing task on server {backend} backend. {len(queue)} jobs in queue.")
    # print(f"Queueing {task} on server {backend} backend. {len(queue)} jobs in queue.")

    job = queue.enqueue(
        _backends[backend].run,
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
        tags=tags,
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
