import requests

########################################################################################


class Provider:
    def __init__(self, url: str = "http://localhost:8000"):
        self.url = url

    @property
    def available_backends(self):
        if hasattr(self, "_available_backends"):
            return self._available_backends
        else:
            return ["qutip", "tensorcircuit"]

    @property
    def registration_url(self):
        return self.url + "/auth/register"

    @property
    def login_url(self):
        return self.url + "/auth/token"

    def job_submission_url(self, backend):
        assert backend in self.available_backends, "Unavailable backend"
        return self.url + "/submit/{}".format(backend)

    def job_retrieval_url(self, job_id):
        return self.url + "/retrieve/{}".format(job_id)

    def job_cancellation_url(self, job_id):
        return self.url + "/cancel/{}".format(job_id)
