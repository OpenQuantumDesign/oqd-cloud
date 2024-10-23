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

from fastapi import APIRouter, HTTPException
from fastapi import status as http_status

from rq.job import Job

from sqlalchemy import select

########################################################################################

from oqd_cloud.server.route.auth import user_dependency, pwd_context
from oqd_cloud.server.model import UserRegistrationForm  # , Job
from oqd_cloud.server.database import UserInDB, JobInDB, db_dependency

from oqd_cloud.server.model import Job  # todo: proper import

########################################################################################

user_router = APIRouter(prefix="/user", tags=["User"])

########################################################################################


async def available_user(user, db):
    query = await db.execute(
        select(UserInDB).filter(UserInDB.username == user.username)
    )
    user_in_db = query.scalars().first()
    if not user_in_db:
        return user

    raise HTTPException(status_code=http_status.HTTP_409_CONFLICT)


########################################################################################


@user_router.post(
    "/register",
    status_code=http_status.HTTP_201_CREATED,
)
async def register_user(create_user_form: UserRegistrationForm, db: db_dependency):
    user = await available_user(create_user_form, db)
    if user:
        user_in_db = UserInDB(
            username=user.username,
            email=user.email,
            hashed_password=pwd_context.hash(user.password),
        )

        db.add(user_in_db)
        await db.commit()
        return {"status": "success"}

    raise HTTPException(status_code=http_status.HTTP_401_UNAUTHORIZED)


@user_router.get("/jobs", tags=["Job"])
async def user_jobs(user: user_dependency, db: db_dependency):
    query = await db.execute(
        select(JobInDB).filter(
            JobInDB.user_id == user.user_id,
        )
    )
    jobs_in_db = query.scalars().all()
    if jobs_in_db:
        return [Job.model_validate(job) for job in jobs_in_db]

    raise HTTPException(status_code=http_status.HTTP_401_UNAUTHORIZED)
