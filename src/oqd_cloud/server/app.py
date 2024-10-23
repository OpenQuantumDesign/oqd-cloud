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

from fastapi import FastAPI
from contextlib import asynccontextmanager

########################################################################################

from oqd_cloud.server.database import engine, Base
from oqd_cloud.server.route import user_router, auth_router, job_router

########################################################################################


@asynccontextmanager
async def create_db(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(lifespan=create_db)
app.include_router(user_router)
app.include_router(auth_router)
app.include_router(job_router)
