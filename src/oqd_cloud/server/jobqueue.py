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

import os

from redis import Redis
from rq import Queue

from sqlalchemy import select

import asyncio

from contextlib import asynccontextmanager

########################################################################################

from oqd_cloud.server.database import get_db, JobInDB

########################################################################################

REDIS_HOST = os.environ["REDIS_HOST"]
REDIS_PASSWORD = os.environ["REDIS_PASSWORD"]

redis_client = Redis(
    host=REDIS_HOST, password=REDIS_PASSWORD, port=6379, decode_responses=False
)
queue = Queue(connection=redis_client)

########################################################################################


async def _report_success(job, connection, result, *args, **kwargs):
    async with asynccontextmanager(get_db)() as db:
        status_update = dict(status="finished", result=result.model_dump_json())
        query = await db.execute(select(JobInDB).filter(JobInDB.job_id == job.id))
        job_in_db = query.scalars().first()
        for k, v in status_update.items():
            setattr(job_in_db, k, v)
        await db.commit()


def report_success(job, connection, result, *args, **kwargs):
    return asyncio.get_event_loop().run_until_complete(
        _report_success(job, connection, result, *args, **kwargs)
    )


async def _report_failure(job, connection, result, *args, **kwargs):
    async with asynccontextmanager(get_db)() as db:
        status_update = dict(status="failed")
        query = await db.execute(select(JobInDB).filter(JobInDB.job_id == job.id))
        job_in_db = query.scalars().first()
        for k, v in status_update.items():
            setattr(job_in_db, k, v)
        await db.commit()


def report_failure(job, connection, result, *args, **kwargs):
    return asyncio.get_event_loop().run_until_complete(
        _report_failure(job, connection, result, *args, **kwargs)
    )


async def _report_stopped(job, connection, result, *args, **kwargs):
    async with asynccontextmanager(get_db)() as db:
        status_update = dict(status="stopped")
        query = await db.execute(select(JobInDB).filter(JobInDB.job_id == job.id))
        job_in_db = query.scalars().first()
        for k, v in status_update.items():
            setattr(job_in_db, k, v)
        await db.commit()


def report_stopped(job, connection, result, *args, **kwargs):
    return asyncio.get_event_loop().run_until_complete(
        _report_stopped(job, connection, result, *args, **kwargs)
    )
