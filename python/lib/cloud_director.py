import logging
import time

from typing import Any, Optional
from lib.requests_session import requests_session
from multiprocessing.pool import ThreadPool

from lxml import objectify
from lxml import etree

log = logging.getLogger(__name__)
pageSize = 128

def wait_for_task(vmware_access_token: str, task: str) -> bool:
    """Wait for a single task to complete

    Args:
        director_url: base director url, eg.: https://fradir01.vmware-solutions.cloud.ibm.com
        vmware_access_token: A VMWare VCD Session token.
        tasks: a list of task href

    Returns:
        Boolean when all tasks have a status of success
    
    Raises:
        requests.RequestException: all Requests package exceptions
            can be raised due to, e.g., connection or authorization errors.
    """

    running_status = ['queued', 'preRunning', 'running' ]
    completed_status = ['success', 'error', 'aborted']

    #Poll each task until status = success

    s = requests_session()
    while(True):

        time.sleep(1)
        headers = {
            "Authorization": f"Bearer {vmware_access_token}",
            "Accept": "application/*+json;version=38.0"
        }

        log.debug(f"Getting task: {task}")

        r = s.get(url=task, headers=headers)
        r.raise_for_status()

        if r.json()["status"] in completed_status:
            break

    return True

def wait_for_tasks(vmware_access_token: str, tasks: list) -> bool:
    """Wait for a list of tasks
    Args:
        director_url: base director url, eg.: https://fradir01.vmware-solutions.cloud.ibm.com
        vmware_access_token: A VMWare VCD Session token.
        tasks: a list of task href
    Returns:
        Boolean when all tasks have a status of success
    
    Raises:
        requests.RequestException: all Requests package exceptions
            can be raised due to, e.g., connection or authorization errors.
    """

    #Create Thread Pool

    if len(tasks) > 0:
        with ThreadPool(len(tasks)) as pool:
            args = [(vmware_access_token, task) for task in tasks]
            results = pool.starmap(wait_for_task, args)

def query_vm(director_url: str, vmware_access_token: str, filter: str) -> dict[str, Any]:
    """List all VM filtered by the a filter

    Args:
        director_url: base director url, eg.: https://fradir01.vmware-solutions.cloud.ibm.com
        vmware_access_token: A VMWare VCD Session token.
        filter: A VCD Query filter, for example, name==virtual_machine_1

    Returns:
       A list of Virtual Machine records
    
    Raises:
        requests.RequestException: all Requests package exceptions
            can be raised due to, e.g., connection or authorization errors.
    """

    # request retry mechanism
    s = requests_session()

    endpoint_url = "/".join([director_url, "api", "query"])

    headers = {
        "Authorization": f"Bearer {vmware_access_token}",
        "Accept": "application/*+json;version=38.1"
    }

    params: dict[str, int | str] = {
        "filter": filter,
        "type": "vm",
        "format": "records",
        "pageSize": pageSize
    }
    
    log.debug(f'Query Virtual Machines with filter: {filter}')

    page_number = 0
    record = []
    more_pages = True

    while(more_pages):
        page_number = page_number + 1
        log.debug(f"Getting page {page_number}")
        params["page"] = page_number

        r = s.get(url=endpoint_url, headers=headers, params=params)
        r.raise_for_status()

        total = r.json()["total"]            
        record = record + r.json()["record"]
        more_pages = page_number*pageSize < total

    return record

def query_catalogs(director_url: str, vmware_access_token: str, filter: str) -> dict[str, Any]:
    """List all VM filtered by the a filter

    Args:
        director_url: base director url, eg.: https://fradir01.vmware-solutions.cloud.ibm.com
        vmware_access_token: A VMWare VCD Session token.
        filter: A VCD Query filter, for example, name==virtual_machine_1

    Returns:
       A list of Virtual Machine records
    
    Raises:
        requests.RequestException: all Requests package exceptions
            can be raised due to, e.g., connection or authorization errors.
    """

    # request retry mechanism
    s = requests_session()

    endpoint_url = "/".join([director_url, "api", "catalogs", "query"])

    headers = {
        "Authorization": f"Bearer {vmware_access_token}",
        "Accept": "application/*+json;version=38.1"
    }

    params: dict[str, int | str] = {
        "filter": filter,
        "type": "catalogs",
        "format": "records",
        "pageSize": pageSize
    }
    
    log.debug(f'Query Catalogs with filter: {filter}')

    page_number = 0
    record = []
    more_pages = True

    while(more_pages):
        page_number = page_number + 1
        log.debug(f"Getting page {page_number}")
        params["page"] = page_number

        r = s.get(url=endpoint_url, headers=headers, params=params)
        r.raise_for_status()

        total = r.json()["total"]            
        record = record + r.json()["record"]
        more_pages = page_number*pageSize < total

    return record

def get_resource(vmware_access_token: str, href: str) -> dict[str, Any]:
    """Get the JSON Record of a resource by HREF

    Args:
        director_url: base director url, eg.: https://fradir01.vmware-solutions.cloud.ibm.com
        vmware_access_token: A VMWare VCD Session token.
        href: THe href of the resource, eg, https://dirw002.eu-de.vmware.cloud.ibm.com/api/vApp/vm-0a782687-a2c2-44df-86f0-fce60e075d7c

    Returns:
        A JSON record of the resource
    
    Raises:
        requests.RequestException: all Requests package exceptions
            can be raised due to, e.g., connection or authorization errors.
    """

    # request retry mechanism
    s = requests_session()

    headers = {
        "Authorization": f"Bearer {vmware_access_token}",
        "Accept": "application/*+json;version=38.1"
    }

    log.debug(f"Retrieving Resource {href}")

    r = s.get(url=href, headers=headers)
    r.raise_for_status()

    return r.json()


def get_vm_metadata(vmware_access_token: str, href: str) -> dict[str, Any]:
    """Get the JSON Record of a VM or VAPP referenced by the provided href/metadata

    Args:
        director_url: base director url, eg.: https://fradir01.vmware-solutions.cloud.ibm.com
        vmware_access_token: A VMWare VCD Session token.
        href: THe href of the resource, eg, https://dirw002.eu-de.vmware.cloud.ibm.com/api/vApp/vm-0a782687-a2c2-44df-86f0-fce60e075d7c

    Returns:
        A metadata record
    
    Raises:
        requests.RequestException: all Requests package exceptions
            can be raised due to, e.g., connection or authorization errors.
    """

    # request retry mechanism
    s = requests_session()

    endpoint_url = "/".join([href, "metadata"])

    headers = {
        "Authorization": f"Bearer {vmware_access_token}",
        "Accept": "application/*+json;version=38.1"
    }

    log.debug(f'Retrieving metadata for {href}')

    r = s.get(url=endpoint_url, headers=headers)
    r.raise_for_status()

    return r.json()

def powerOff(href: str, vmware_access_token: str) -> dict[str, Any]:
    """Perform an Power Off operation on a VM or VAPP

    Args:
        href: Resource reference, eg, https://dirw002.eu-de.vmware.cloud.ibm.com/api/vApp/vm-0a782687-a2c2-44df-86f0-fce60e075d7c
        vmware_access_token: A VMWare VCD Session token.

    Returns:
        A task object
    
    Raises:
        requests.RequestException: all Requests package exceptions
            can be raised due to, e.g., connection or authorization errors.
    """

    # request retry mechanism
    s = requests_session()

    endpoint_url = "/".join([href, "power", "action", "powerOff"])

    headers = {
        "Authorization": f"Bearer {vmware_access_token}",
        "Accept": "application/*+json;version=38.0",
    }

    log.debug(f'Power Off: {href}')
    r = s.post(url=endpoint_url, headers=headers)
    r.raise_for_status()

    return r.json()

def powerOn(href: str, vmware_access_token: str) -> dict[str, Any]:
    """Perform an Power On operation on a VM or VAPP

    Args:
        href: Resource reference, eg, https://dirw002.eu-de.vmware.cloud.ibm.com/api/vApp/vm-0a782687-a2c2-44df-86f0-fce60e075d7c
        vmware_access_token: A VMWare VCD Session token.

    Returns:
        A task object
    
    Raises:
        requests.RequestException: all Requests package exceptions
            can be raised due to, e.g., connection or authorization errors.
    """

    # request retry mechanism
    s = requests_session()

    endpoint_url = "/".join([href, "power", "action", "powerOn"])

    headers = {
        "Authorization": f"Bearer {vmware_access_token}",
        "Accept": "application/*+json;version=38.0",
    }

    log.debug(f'Power On: {href}')
    r = s.post(url=endpoint_url, headers=headers)
    r.raise_for_status()

    return r.json()

def create_catalog_item(catalog_href: str, vmware_access_token: str, item_name: str) -> dict[str, Any]:
    """Add an item to a Catalog
    Args:
        catalog_href: HREF to a catalog eg. https://dirw002.eu-de.vmware.cloud.ibm.com/api/catalog/35a720ad-2b98-4706-b9a2-739b65af7965
        vmware_access_token: A VMWare VCD Session token.
        item_name: Name of the item to upload

    Returns:
        A Catalog Item object
    
    Raises:
        requests.RequestException: all Requests package exceptions
            can be raised due to, e.g., connection or authorization errors.
    """

    # Generate Payload

    E = objectify.ElementMaker(
            annotate=False,
            namespace = 'http://www.vmware.com/vcloud/v1.5',
            nsmap = {
                None: 'http://www.vmware.com/vcloud/v1.5',
                'ovf': 'http://schemas.dmtf.org/ovf/envelope/1'
            }
        )

    endpoint_url = "/".join([catalog_href, "action", "upload"])

    body = E.UploadVAppTemplateParams(name=item_name)
    body.append(E.Description('Created by automation'))

    log.debug(f"Composing VAPPTemplate: {item_name}")

    s = requests_session()

    headers = {
        "Authorization": f"Bearer {vmware_access_token}",
        "Accept": "application/*+json;version=38.0",
        "Content-Type": "application/vnd.vmware.vcloud.uploadVAppTemplateParams+xml"
    }

    r = s.post(url=endpoint_url, headers=headers, data=etree.tostring(body, xml_declaration=True) )
    r.raise_for_status()

    return r.json()


def create_catalog(director_url: str, vmware_access_token: str, org_id: str, catalog_name: str) -> dict[str, Any]:
    """Create a Catalog on an org
    Args:
        director_url: Main director URL eg. https://dirw002.eu-de.vmware.cloud.ibm.com/
        vmware_access_token: A VMWare VCD Session token.
        org_id: The id of an organization
        catalog_name: The name of the new catalog

    Returns:
        A task object
    
    Raises:
        requests.RequestException: all Requests package exceptions
            can be raised due to, e.g., connection or authorization errors.
    """

    # Generate Payload

    E = objectify.ElementMaker(
            annotate=False,
            namespace = 'http://www.vmware.com/vcloud/v1.5',
            nsmap = {
                None: 'http://www.vmware.com/vcloud/v1.5'
            }
        )

    endpoint_url = "/".join([director_url, "api", "admin", "org", org_id, "catalogs"])

    body = E.AdminCatalog(name=catalog_name)
    body.append(E.Description('Created via Automation'))

    log.debug(f"Creating  catalog: {catalog_name}")
    s = requests_session()

    headers = {
        "Authorization": f"Bearer {vmware_access_token}",
        "Accept": "application/*+json;version=38.0",
        "Content-Type": "application/vnd.vmware.admin.catalog+xml",
    }

    r = s.post(url=endpoint_url, headers=headers, data=etree.tostring(body, xml_declaration=True) )
    r.raise_for_status()

    return r.json()


def create_apitoken(director_url: str, vmware_access_token: str, org: str, org_id: str, token_name: str) -> str:
    """Generate a API Token name, return the token value as a string, zero length string means
       failure.

    Args:
        director_url: Main director URL eg. https://dirw002.eu-de.vmware.cloud.ibm.com/
        vmware_access_token: A VMWare VCD Session token.
        org: The name of an organization
        org_id: the ID of an ORG
        token_name: The name of the API Token

    Returns:
        A VMWare VCD Refresh Token
    
    Raises:
        requests.RequestException: all Requests package exceptions
            can be raised due to, e.g., connection or authorization errors.
    """

    # Generate Payload

    endpoint_url = "/".join([director_url, "oauth", "tenant", org, "register"])

    log.debug(f"Registering a new token: {token_name}")
    s = requests_session()

    body = {"client_name":token_name}

    headers = {
        "Authorization": f"Bearer {vmware_access_token}",
        "Accept": "application/json;version=38.1",
        "Content-Type": "application/json",
        "X-VMWARE-VCLOUD-AUTH-CONTEXT": org,
        "X-VMWARE-VCLOUD-TENANT-CONTEXT": org_id,
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-AU,en;q=0.9"
    }

    # Make initial call to Register
    r = s.post(url=endpoint_url, headers=headers, json=body)
    r.raise_for_status()

    # Construct the token request

    endpoint_url = "/".join([director_url, "oauth", "tenant", org, "token"])

    headers = {
        "Authorization": f"Bearer {vmware_access_token}",
        "Accept": "application/json;version=38.1",
        "Content-Type": "application/x-www-form-urlencoded",
        "X-VMWARE-VCLOUD-AUTH-CONTEXT": org,
        "X-VMWARE-VCLOUD-TENANT-CONTEXT": org_id,
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-AU,en;q=0.9"
    }

    body = {"MIME Type": "application/x-www-form-urlencoded",
            "grant_type": r.json()['grant_types'][0],
            "client_id": r.json()['client_id'],
            "assertion": vmware_access_token} 
    
    r = s.post(url=endpoint_url, headers=headers, data=body)
    r.raise_for_status()

    return r.json()["refresh_token"]
    

def upload_ovf(director_url: str, vmware_access_token: str, catalog_id: str, ovf_url: str, item_name: str) -> dict[str, Any]:
    """Create a catalog item
    Args:
        director_url: Main director URL eg. https://dirw002.eu-de.vmware.cloud.ibm.com/
        vmware_access_token: A VMWare VCD Session token.
        catalog_id: The id of the catalog to create the item in
        ovf_url: The URl of the catalog item, eg,
                  https://s3.us-east.cloud-object-storage.appdomain.cloud/vcfaas-lab-images/ibm-vcfaas-lab-apache2.ovf
        item_name: The name of the new catalog item

    Returns:
        A CatalogItem object
    
    Raises:
        requests.RequestException: all Requests package exceptions
            can be raised due to, e.g., connection or authorization errors.
    """

    # Generate Payload

    E = objectify.ElementMaker(
            annotate=False,
            namespace = 'http://www.vmware.com/vcloud/v1.5',
            nsmap = {
                'root': 'http://www.vmware.com/vcloud/v1.5'
            }
    )

    body = E.UploadVAppTemplateParams(name=item_name, sourceHref=ovf_url)
    body.append(E.Description('Created via Automation'))


    endpoint_url = "/".join([director_url, "api", "catalog", catalog_id, "action", "upload"])

    headers = {
        "Authorization": f"Bearer {vmware_access_token}",
        "Accept": "application/*+json;version=38.0",
        "Content-Type": "application/vnd.vmware.vcloud.uploadVAppTemplateParams+xml",
    }

    log.debug(f"Uploading OVF to catalog: {ovf_url}")
    s = requests_session()

    r = s.post(url=endpoint_url, headers=headers, data=etree.tostring(body, xml_declaration=True) )
    r.raise_for_status()

    return r.json()
