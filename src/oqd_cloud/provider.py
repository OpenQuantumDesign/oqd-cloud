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

import requests 
from oqd_cloud.server.model import Backends


class Provider:
    def __init__(self, host: str = "http://localhost", port: int = 8000):
        """

        Args:
            url: URL for the server
        """
        url = f"{host}:{port}"
        self.url = url

        # get available backends
        self.backends = Backends(available=[])
        response = requests.get(
            self.url + "/available_backends"
        )
        backends = Backends.model_validate(response.json())
        if response.status_code == 200:
            self.backends = backends

    @property
    def available_backends(self):
        return self.backends.available
    
    @property
    def registration_url(self):
        return self.url + "/auth/register"

    @property
    def login_url(self):
        return self.url + "/auth/token"

    def job_submission_url(self, backend):
        assert backend in self.available_backends, "Unavailable backend"
        return self.url + f"/submit/{backend}"

    def job_retrieval_url(self, job_id):
        return self.url + f"/retrieve/{job_id}"

    def job_cancellation_url(self, job_id):
        return self.url + f"/cancel/{job_id}"
