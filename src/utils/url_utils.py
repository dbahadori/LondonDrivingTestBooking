import os
import logging
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from urllib.parse import urlparse


class URLChecker:
    def __init__(self, retries=3, backoff_factor=1, status_forcelist=None):
        if status_forcelist is None:
            status_forcelist = [500, 502, 503, 504]
        retry_strategy = Retry(
            total=retries,
            backoff_factor=backoff_factor,
            status_forcelist=status_forcelist
        )
        self.http = requests.Session()
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.http.mount("http://", adapter)
        self.http.mount("https://", adapter)
    @staticmethod
    def extract_domain(base_url):
        """Extract the domain from the base URL."""
        parsed_url = urlparse(base_url)
        domain_with_subdomain = parsed_url.netloc

        if '.com' in domain_with_subdomain:
            return domain_with_subdomain.split('.com')[0]
        elif '.ir' in domain_with_subdomain:
            return domain_with_subdomain.split('.ir')[0]
        else:
            return domain_with_subdomain  # Fallback if no valid TLD is found

    def is_url_available(self, url):
        """Check if the URL is available by sending a GET request."""
        try:
            response = self.http.get(url, timeout=5)
            logging.info(f"Checked URL: {url}, Status: {response.status_code}")
            return response.status_code == 200
        except requests.RequestException as e:
            logging.error(f"Error accessing {url}: {e}")
            return False
