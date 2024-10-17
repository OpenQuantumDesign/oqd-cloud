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

#  Copyright 2023-2024 Open Quantum Design
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from typing import Literal, Optional
from pydantic import BaseModel, ConfigDict
import requests

from core.backend.task import Task
from cloud.provider import Provider


__all__ = ["Job", "Client"]


class Job(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    job_id: str
    task: str
    backend: str
    status: str
    result: Optional[str] = None
    user_id: str


class Client:
    def __init__(self):
        self._jobs = {}

    @property
    def jobs(self):
        return self._jobs

    def __len__(self):
        return len(self.jobs)

    @property
    def pending(self):
        return self.status_report["queued"]["count"] > 0

    @property
    def status_report(self):
        _status_report = dict(
            queued=dict(count=0, jobs=[]),
            finished=dict(count=0, jobs=[]),
            failed=dict(count=0, jobs=[]),
            stopped=dict(count=0, jobs=[]),
            canceled=dict(count=0, jobs=[]),
        )
        for job in self.jobs.values():
            _status_report[job.status]["count"] += 1
            _status_report[job.status]["jobs"].append(job)
        return _status_report

    @property
    def provider(self):
        if hasattr(self, "_provider"):
            return self._provider
        raise ConnectionError("Missing provider")

    @property
    def token(self):
        if hasattr(self, "_token"):
            return self._token
        raise ConnectionError("Missing token")

    @property
    def authorization_header(self):
        return dict(
            Authorization="{} {}".format(
                self.token["token_type"], self.token["access_token"]
            )
        )

    def connect(self, provider: Provider, username: str, password: str):
        self._provider = provider

        # username = input("Enter username: ")
        # password = input("Enter password: ")
        login = dict(username=username, password=password)

        response = requests.post(
            provider.login_url,
            data=login,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        if response.status_code == 200:
            self._token = response.json()
            return

        raise response.raise_for_status()

    # def reconnect(self):
    #     self.connect(self, self.provider)
    #     pass

    def submit_job(self, task: Task, backend: Literal["analog-qutip",]):
        response = requests.post(
            self.provider.job_submission_url(backend=backend),
            json=task.model_dump(),
            headers=self.authorization_header,
        )
        job = Job.model_validate(response.json())

        if response.status_code == 200:
            self._jobs[job.job_id] = job
            return self.jobs[job.job_id]

        raise response.raise_for_status()

    def retrieve_job(self, job_id):
        response = requests.get(
            self.provider.job_retrieval_url(job_id=job_id),
            headers=self.authorization_header,
        )
        job = Job.model_validate(response.json())

        if response.status_code == 200:
            self._jobs[job_id] = job
            return self.jobs[job_id]

        raise response.raise_for_status()

    def status_update(self):
        for job_id in self.jobs.keys():
            self.retrieve_job(job_id)
        pass

    def resubmit_job(self, job_id):
        return self.submit_job(
            task=Task.model_validate_json(self.jobs[job_id].task),
            backend=self.jobs[job_id].backend,
        )

    def cancel_job(self, job_id):
        response = requests.delete(
            self.provider.job_cancellation_url(job_id=job_id),
            headers=self.authorization_header,
        )
        job = Job.model_validate(response.json())
        print(job.status)

        if response.status_code == 200:
            self._jobs[job_id] = job
            return self.jobs[job_id]

        raise response.raise_for_status()
