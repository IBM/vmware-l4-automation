"""Module with IBM Cloud IAM Identity Service API calls.

The IAM Identity Service API is used to manage service IDs, API key identities,
trusted profiles, account security settings, and to create IAM access tokens
for a user or service ID.

https://cloud.ibm.com/apidocs/iam-identity-token-api
"""

import logging

from lib.requests_session import requests_session
from typing import Any

log = logging.getLogger(__name__)


def request_ibm_iam_access_token(ibm_api_key: str) -> str:
    """The API call to get an IBM Cloud IAM access token.

    Args:
        ibm_api_key: IBM IAM API key.

    Returns:
        IBM IAM access token.

    Raises:
        requests.RequestException: all Requests package exceptions
            can be raised due to, e.g., connection or authorization errors.
    """

    # request retry mechanism
    s = requests_session()

    endpoint_url = "/".join(["https://iam.cloud.ibm.com", "identity", "token"])

    payload = {
        "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
        "apikey": ibm_api_key,
    }

    log.debug("Request IBM Cloud IAM access token.")
    r = s.post(url=endpoint_url, data=payload)
    r.raise_for_status()
    log.debug(f'Got IBM Cloud IAM access token: {r.json()["access_token"][:7]}(...)')

    return r.json()["access_token"]

def ibm_iam_apikey_details(ibm_api_key: str, ibm_iam_access_token: str) -> dict[str, Any]:
    """The API call to get the details of an API Key

        https://cloud.ibm.com/apidocs/iam-identity-token-api#get-api-keys-details

    Args:
        ibm_api_key: IBM IAM API key.

    Returns:
        IBM IAM access token.

    Raises:
        requests.RequestException: all Requests package exceptions
            can be raised due to, e.g., connection or authorization errors.
    """

    # request retry mechanism
    s = requests_session()

    endpoint_url = "https://iam.cloud.ibm.com/v1/apikeys/details"

    headers = {"authorization": f"Bearer {ibm_iam_access_token}",
               "IAM-Apikey": ibm_api_key,
               "Content-Type": "application/json"}

    log.debug("Request Detilas for an API Key.")
    r = s.get(url=endpoint_url, headers=headers)
    r.raise_for_status()
    log.debug(f'Got IBM Cloud IAM access token Details: {r.json()}')

    return r.json()
