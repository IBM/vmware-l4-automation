"""Module with IBM Cloud VMware Cloud Foundation (VCF) as a Service API calls.

https://cloud.ibm.com/apidocs/vmware-service#list-director-sites
"""


import logging
from typing import Any

from lib.requests_session import requests_session

log = logging.getLogger(__name__)


def list_director_sites(ibm_iam_access_token: str, region: str) -> dict[str, Any]:
    """List Cloud Director site instances.

    List all VMware Cloud Director site instances the user can access
    in the cloud account.

    Args:
        ibm_iam_access_token: IBM IAM access token.
        region: VCF as a Service Director region, e.g., "eu-fr2".

    Returns:
        Dictionary with VMware Cloud Director site instances.
    
    Raises:
        requests.RequestException: all Requests package exceptions
            can be raised due to, e.g., connection or authorization errors.
    """
    s = requests_session()

    base_url = f"https://api.{region}.vmware.cloud.ibm.com"

    endpoint_url = "/".join([base_url, "v1", "director_sites"])

    headers = {"authorization": f"Bearer {ibm_iam_access_token}"}

    log.debug("Request VCFaaS Director sites.")
    r = s.get(url=endpoint_url, headers=headers)
    r.raise_for_status()
    log.debug(f'Got {len(r.json()["director_sites"])} VCFaaS Director sites.')

    return r.json()

def get_director_site(ibm_iam_access_token: str, region: str, site_id: str) -> dict[str, Any]:
    """Get a director site based on its ID

    Args:
        ibm_iam_access_token: IBM IAM access token.
        region: VCF as a Service Director region, e.g., "eu-fr2".
        site_id: The site id for example 40e701cd-ef86-4d5e-a847-e7c336f11f27

    Returns:
        Dictionary with VMware Cloud Director site instances.
    
    Raises:
        requests.RequestException: all Requests package exceptions
            can be raised due to, e.g., connection or authorization errors.
    """
    s = requests_session()

    base_url = f"https://api.{region}.vmware.cloud.ibm.com"

    endpoint_url = "/".join([base_url, "v1", "director_sites", site_id])

    headers = {"authorization": f"Bearer {ibm_iam_access_token}"}

    log.debug("Get a VCFaaS site")
    r = s.get(url=endpoint_url, headers=headers)
    r.raise_for_status()
    #log.debug(f'Got {len(r.json()["director_sites"])} VCFaaS Director sites.')

    return r.json()


def get_vmware_access_token(ibm_iam_access_token: str, url: str, org: str) -> str:
    """Retreive a VMWare Cloud Director session token represent in the X-VMWARE-VCLOUD-ACCESS-TOKEN header.

    Args:
        ibm_iam_access_token : An IBM IAM Session key
        url: Director site base URL, eg, https://dirw002.eu-de.vmware.cloud.ibm.com
        org: The organization the Director Site is a memeber of

    Returns:
        A VMWare VCD Access Token to be used in future API calls to VCD
    
    Raises:
        requests.RequestException: all Requests package exceptions
            can be raised due to, e.g., connection or authorization errors.
    """

   # request retry mechanism
    s = requests_session()

    endpoint_url = "/".join([url, "cloudapi", "1.0.0", "sessions"])

    headers = {"Authorization": f"Bearer {ibm_iam_access_token}; org={org}",
               "Accept": "application/*;version=39.0"}

    log.debug("Requesting VMWare Access Token")
    r = s.post(url=endpoint_url, headers=headers)
    r.raise_for_status()

    return r.headers["X-VMWARE-VCLOUD-ACCESS-TOKEN"]


def list_vcfaas_vdcs(ibm_iam_access_token: str, region: str) -> dict[str, Any]:
    """Retreive all VDC's for a specific region

    Args:
        ibm_iam_access_token: IBM IAM access token.
        region: VCF as a Service Director region, e.g., "eu-fr2".

    Returns:
        A json list of Virtual Data Centers
    
    Raises:
        requests.RequestException: all Requests package exceptions
            can be raised due to, e.g., connection or authorization errors.
    """

   # request retry mechanism
    s = requests_session()

    base_url = f"https://api.{region}.vmware.cloud.ibm.com"

    endpoint_url = "/".join([base_url, "v1", "vdcs"])

    headers = {"authorization": f"Bearer {ibm_iam_access_token}",
               "Content-Type": "application/json"}
    
    log.debug("Retrieving list of VDC")
    r = s.get(url=endpoint_url, headers=headers)
    r.raise_for_status()
    return r.json()

def create_vdc(ibm_iam_access_token: str, region: str, director_site_id: str,
               pvdc_id: str, vdc_name: str, resource_group_id: str, cpu: int = 1, ram: int = 1,
               edge: bool = False) -> dict[str, Any]:
    """Create a Virtual Data Center as a reserved type.

    Args:
        ibm_iam_access_token: IBM IAM access token.
        region: VCF as a Service Director region, e.g., "eu-fr2".
        director_site_id: Director Site ID.
        pvdc_id: Provider Virtual Data Center ID.
        vdc_name: VDC name to be created.
        cpu: No. of CPUs to be reserved for VDC.
        ram: No. of Memory to be reserved for VDC.
        edge: Should it have edge capabilities.
        resource_group_id: ID Of an IBM Cloud Resource Group.

    Returns:
        Dictionary with VDC metadata after creation request.
    
    Raises:
        requests.RequestException: all Requests package exceptions
            can be raised due to, e.g., connection or authorization errors.
    """
    # request retry mechanism
    s = requests_session()

    base_url = f"https://api.{region}.vmware.cloud.ibm.com"
    endpoint_url = "/".join([base_url, "v1", "vdcs"])

    headers = {"authorization": f"Bearer {ibm_iam_access_token}",
               "Content-Type": "application/json"}
    
    payload = {
        "name": vdc_name,
        "cpu": cpu,
        "ram": ram,
        "resource_group": {"id": resource_group_id},
        "director_site": {
            "id": director_site_id,
            "pvdc": {
                "id": pvdc_id,
                "provider_type": {
                    "name": "on_demand"
                }
            }
        }
    }


    if edge:
        payload["edge"] = {"type": "efficiency"}

    log.debug(f"Request create VDC {vdc_name}")
    r = s.post(url=endpoint_url, headers=headers, json=payload)
    r.raise_for_status()
    log.debug(f"VDC {vdc_name} create requested.")

    return r.json()



def delete_vdc(ibm_iam_access_token: str, region: str, vdc_id: str) -> dict[str, Any]:
    """Delete a Virtual Data Center

    Args:
        ibm_iam_access_token: IBM IAM access token.
        region: VCF as a Service Director region, e.g., "eu-fr2".
        vdc_id: ID of the VDC to delete

    Returns:
        Dictionary with VDC metadata after deletion request.
    
    Raises:
        requests.RequestException: all Requests package exceptions
            can be raised due to, e.g., connection or authorization errors.
    """

    # request retry mechanism
    s = requests_session()

    base_url = f"https://api.{region}.vmware.cloud.ibm.com"
    endpoint_url = "/".join([base_url, "v1", "vdcs", vdc_id])
    headers = {"authorization": f"Bearer {ibm_iam_access_token}"}

    log.debug(f"Request delete VDC {vdc_id}")
    r = s.delete(url=endpoint_url, headers=headers)
    r.raise_for_status()
    log.debug(f"VDC {vdc_id} delete requested.")

    return r.json()

def get_org_id(ibm_iam_access_token: str, director_url: str, org: str) -> str:
    """Get the ORG ID 

    Args:
        ibm_iam_access_token : An IBM IAM Session key
        director: Director site base URL, eg, https://dirw002.eu-de.vmware.cloud.ibm.com
        org: The organization the Director Site is a memeber of

    Returns:
        the org id
    
    Raises:
        requests.RequestException: all Requests package exceptions
            can be raised due to, e.g., connection or authorization errors.
    """

   # request retry mechanism
    s = requests_session()

    endpoint_url = "/".join([director_url, "cloudapi", "1.0.0", "sessions"])

    headers = {"Authorization": f"Bearer {ibm_iam_access_token}; org={org}",
               "Accept": "application/*;version=39.0"}

    log.debug("Getting ORG ID for {org}")
    r = s.post(url=endpoint_url, headers=headers)
    r.raise_for_status()
    return r.json()['org']['id'].split(':')[-1]