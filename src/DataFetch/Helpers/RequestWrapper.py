import requests as r
import time
from fake_useragent import UserAgent
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Request(r.Session):
    def __init__(self, sleep_time: float = 5.0, max_retries: int = 3):
        """
        Initialize the Request session with a fake User-Agent, sleep time between requests, and maximum retries.

        Args:
            sleep_time (float): Minimum time to wait between requests.
            max_retries (int): Maximum number of retries for failed requests.
        """
        super(Request, self).__init__()
        self.ua = UserAgent()
        self.update_headers()
        self.sleep_time = sleep_time
        self.last_request = 0.0
        self.max_retries = max_retries

    def update_headers(self):
        """Update the headers to include a fake User-Agent."""
        self.headers.update({'User-Agent': str(self.ua.chrome)})

    def make_request(self, method, url, timeout=30, **kwargs):
        """
        Make an HTTP request with the specified method, URL, and timeout, retrying on failure.

        Args:
            method (str): HTTP method to use (e.g., 'GET', 'POST').
            url (str): URL to request.
            timeout (int): Timeout for the request in seconds.
            **kwargs: Additional arguments to pass to the request.

        Returns:
            requests.Response: The response object from the request.

        Raises:
            requests.exceptions.RequestException: If the request fails after the maximum number of retries.
        """
        # If the request is too new, sleep until enough time has passed
        rem_sleep_time = self.sleep_time - (time.time() - self.last_request)
        if rem_sleep_time > 0:
            time.sleep(rem_sleep_time)

        attempt = 0
        while attempt < self.max_retries:
            try:
                response = super(Request, self).request(method, url, timeout=timeout, **kwargs)
                self.last_request = time.time()
                return response
            except (r.exceptions.Timeout, r.exceptions.ConnectionError, r.exceptions.ChunkedEncodingError) as e:
                logger.warning(f'Attempt {attempt + 1}/{self.max_retries} failed: {e}')
                time.sleep(timeout)
                attempt += 1

        raise r.exceptions.RequestException(f"Failed to retrieve {url} after {self.max_retries} attempts")

    def get(self, url, **kwargs):
        """Perform a GET request."""
        return self.make_request('GET', url, **kwargs)

    def post(self, url, **kwargs):
        """Perform a POST request."""
        return self.make_request('POST', url, **kwargs)

    def put(self, url, **kwargs):
        """Perform a PUT request."""
        return self.make_request('PUT', url, **kwargs)

    def delete(self, url, **kwargs):
        """Perform a DELETE request."""
        return self.make_request('DELETE', url, **kwargs)

    def patch(self, url, **kwargs):
        """Perform a PATCH request."""
        return self.make_request('PATCH', url, **kwargs)

# Usage example:
# request_session = Request(sleep_time=5.0, max_retries=3)
# response = request_session.get('https://example.com')
# print(response.text)
