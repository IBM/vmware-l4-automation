"""Module to handle IBM Cloud Schematics 

https://cloud.ibm.com/apidocs/schematics/schematics#authentication
https://us-east.schematics.cloud.ibm.com

"""

import logging

from lib.requests_session import requests_session
from typing import Any

log = logging.getLogger(__name__)


def ibm_schematics_list_workspaces(ibm_iam_access_token: str, resource_group: str) -> dict[str, Any]:
    """The API call to list schematics workspaces

       https://cloud.ibm.com/apidocs/schematics/schematics#list-workspaces

    Args:
        ibm_iam_access_token: IBM IAM access token.

    Returns:
        A list of schematics workspaces.

    Raises:
        requests.RequestException: all Requests package exceptions
            can be raised due to, e.g., connection or authorization errors.
    """

    # request retry mechanism
    s = requests_session()

    endpoint_url = "https://schematics.cloud.ibm.com/v1/workspaces"

    headers = {"authorization": f"Bearer {ibm_iam_access_token}"}

    if len(resource_group) > 0:
        headers["resource_group"] = resource_group


    log.debug(f'Request schematicss workspaces with Resource Group: {resource_group}')
    r = s.get(url=endpoint_url, headers=headers)
    r.raise_for_status()
    log.debug(f'Got Schematics workspaces.')

    return r.json()

def ibm_schematics_create_workspace(ibm_iam_access_token: str, resource_group: str, workspace_name: str, description: str,
                                    template_repo: str, folder: str, type: str, variablestore: dict[str, Any]) -> dict[str, Any]:
    """The API call to Create a schematics workspaces
        https://cloud.ibm.com/apidocs/schematics/schematics#create-workspace

    Args:
        ibm_iam_access_token: IBM IAM access token.
        resource_group: ID of the resource group
        workspace_name: A descriptive name of the template
        description: A description of the workspace
        template_repo: The GIT repo for the template.
        folder: The folder within the repo, use "." for current
        variablestore: An list of dict describing hard coded values for the workspace.
                        {name, secure, value, type, description}
        type: The teraform type, eg, terraform_v1.6

    Returns:
        A Schematics STATUS record - 

    Raises:
        requests.RequestException: all Requests package exceptions
            can be raised due to, e.g., connection or authorization errors.
    """
    
    s = requests_session()

    endpoint_url = "https://schematics.cloud.ibm.com/v1/workspaces"
    headers = {"authorization": f"Bearer {ibm_iam_access_token}"}

    payload = {
        "name": workspace_name,
        "type": [
            type
        ],
        "location": "us-south",
        "description": description,
        "resource_group": resource_group,
        "tags": [
            
        ],
        "template_repo": {
            "url": template_repo
        },
        "template_data": [
            {
                "folder": folder,
                "type": type,
                "compact": True,
                "variablestore": variablestore
            }
        ]
    }

    log.debug(f'Creating Schematics Workspace - {workspace_name}')
    r = s.post(url=endpoint_url, headers=headers, json=payload)
    r.raise_for_status()

def ibm_schematics_update_workspace_variables(ibm_iam_access_token: str, workspace_id: str, template_id: str, variablestore: dict[str, Any]) -> dict[str, Any]:
    """The API call to Update an existing workspace variablestore
        https://cloud.ibm.com/apidocs/schematics/schematics#replace-workspace

    Args:
        ibm_iam_access_token: IBM IAM access token.
        workspace_id: ID of an existing workspace
        template_id: ID of an existing template dataa within the repo
        variablestore: An list of dict describing hard coded values for the workspace.
                        {name, secure, value, type, description}

    Returns:
        A Schematics STATUS record - 

    Raises:
        requests.RequestException: all Requests package exceptions
            can be raised due to, e.g., connection or authorization errors.
    """
    
    s = requests_session()
    base_url = "https://schematics.cloud.ibm.com/v1/workspaces"

    endpoint_url = "/".join([base_url, workspace_id, "template_data", template_id, "values"])
    headers = {"authorization": f"Bearer {ibm_iam_access_token}"}

    payload = {"variablestore": variablestore}

    log.debug(f'Updating Workspace - {workspace_id}')
    r = s.put(url=endpoint_url, headers=headers, json=payload)
    r.raise_for_status()

    return r.json()