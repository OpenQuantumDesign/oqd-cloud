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


class Provider:
    def __init__(self, url: str = "http://localhost:8000"):
        """

        Args:
            url: URL for the server
        """
        self.url = url

    @property
    def available_backends(self):
        # todo: get available backends from url
        if hasattr(self, "_available_backends"):
            return self._available_backends
        else:
            return [
                "analog-qutip",
            ]

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
