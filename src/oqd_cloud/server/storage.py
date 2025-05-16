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

from minio import Minio
import os
import io
from datetime import timedelta

from oqd_cloud.server.database import JobInDB

########################################################################################

minio_client = Minio(
    "localhost:9000",
    access_key=os.getenv("MINIO_ROOT_USER"),
    secret_key=os.getenv("MINIO_ROOT_PASSWORD"),
    secure=False,
)

DEFAULT_MINIO_BUCKET = os.getenv("MINIO_DEFAULT_BUCKETS")
RESULT_FILENAME = "result.json"

if not minio_client.bucket_exists(DEFAULT_MINIO_BUCKET):
    minio_client.make_bucket(DEFAULT_MINIO_BUCKET)
    print("Created bucket", DEFAULT_MINIO_BUCKET)
else:
    print("Bucket", DEFAULT_MINIO_BUCKET, "already exists")


def save_obj(job: JobInDB, result):
    # if the file is already saved, fput can be used
    # minio_client.fput_object(
    #     BUCKET, destination_file, source_file,
    # )

    # here we dump to json, todo: future version should dump to HDF5
    json_bytes = result.model_dump_json().encode("utf-8")
    buffer = io.BytesIO(json_bytes)

    minio_client.put_object(
        DEFAULT_MINIO_BUCKET,
        f"{job.id}/{RESULT_FILENAME}",
        data=buffer,
        length=len(json_bytes),
        content_type="application/json",
    )

    return


def get_temp_link(job: JobInDB):
    return minio_client.get_presigned_url(
        "GET",
        DEFAULT_MINIO_BUCKET,
        f"{job.id}/{RESULT_FILENAME}",
        expires=timedelta(hours=2),
    )
