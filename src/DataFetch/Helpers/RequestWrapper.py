import requests as r
import time
from fake_useragent import UserAgent

# A request class modified with embedded fake chrome user agent and a sleep time option between requests.
class Request(r.Session):

    def __init__(self, sleep_time:float=5.0):
        super(Request, self).__init__()
        # Set the header to fake browser agent
        ua = UserAgent()
        self.headers = {'User-Agent':str(ua.chrome)}
        # Set the request time keeper
        self.sleep_time = sleep_time
        self.last_request = 0.0


    def get(self, url, timeout=30, **kwargs):
        # If the request is too new, sleep until enough time has passed
        rem_sleep_time = self.sleep_time - (time.time() - self.last_request)
        if rem_sleep_time > 0:
            time.sleep(rem_sleep_time)
        # Make the request with timeout
        request_obtained = False
        while not request_obtained:
            try:
                result = super(Request, self).get(url, timeout=timeout, **kwargs)
                request_obtained = True
            except r.exceptions.Timeout:
                print('Request timed out: ', url)
            except r.exceptions.ConnectionError:
                print('Request timed out: ', url)
            except r.exceptions.ChunkedEncodingError:
                print('Request forcibly closed: ', url)
                time.sleep(timeout)

        self.last_request = time.time()
        return result