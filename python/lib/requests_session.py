import requests
import urllib3


class TimeoutHTTPAdapter(requests.adapters.HTTPAdapter):
    """Timeout and retry custom Transport Adapter"""

    def send(
        self, request, stream=False, timeout=None, verify=True, cert=None, proxies=None
    ):
        """Sends PreparedRequest object. Returns Response object."""
        self.max_retries = urllib3.util.Retry(
            total=4,
            backoff_factor=7,
            allowed_methods={"GET", "POST", "PUT"},
            status_forcelist={500, 501, 502, 503, 504, 505, 506, 507, 509, 510, 511},
        )
        self.DEFAULT_BACKOFF_MAX=30*60
        return super().send(
            request, stream=False, timeout=180, verify=True, cert=None, proxies=None
        )


def requests_session() -> requests.Session:
    """Request Session definition.

    Returns:
        requests Session object.
    """
    s = requests.Session()
    s.mount("https://", TimeoutHTTPAdapter())

    return s
