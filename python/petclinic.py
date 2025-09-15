import argparse
import os
import json
import re
import uuid

import lib.iam as iam
import lib.vcfaas as vcfass
import lib.cloud_director as cloud_director
import lib.schematics as schematics

from urllib.parse import urlparse
from types import SimpleNamespace
from netaddr import IPNetwork, IPAddress

schematics_catalog = {
    "petclinic" : {"folder": "tf-vdc-configure-v2",
          "github": "https://github.ibm.com/IAAS-Solutions/vcfaaslab",
          "workspace" : "vcfaas_lab01"}
}

lab_catalog = "PetClinic"
lab_terraform = "petclinic"
catalog_items = ["ibm-vcfaas-lab-apache2", "ibm-vcfaas-lab-mysql", "ibm-vcfaas-lab-tomcat"]
lab_catalog_items = {
        "ibm-vcfaas-lab-apache2": "https://s3.us-east.cloud-object-storage.appdomain.cloud/vcfaas-lab-images/ibm-vcfaas-lab-apache2.ovf",
        "ibm-vcfaas-lab-mysql": "https://s3.us-east.cloud-object-storage.appdomain.cloud/vcfaas-lab-images/ibm-vcfaas-lab-mysql.ovf",
        "ibm-vcfaas-lab-tomcat": "https://s3.us-east.cloud-object-storage.appdomain.cloud/vcfaas-lab-images/ibm-vcfaas-lab-tomcat.ovf"}

def parse_arg() -> argparse.Namespace:
    """Parse input arguments.

    Returns:
        argparse object with parsed arguments.
    """

    parser = argparse.ArgumentParser(prog=os.path.basename(__file__))

    parser.add_argument("-k", dest="ibmcloud_api_key", help="IBM Cloud API Key", required=True)
    parser.add_argument("-r", dest="ibmcloud_region", help="IBM Cloud Region", required=True)
    parser.add_argument("-s", dest="director_site_name", help="VCFaaS Site Name", required=True)
    parser.add_argument("-v", dest="vdc_name", help="Virtual Data Center Name", required=True)


    return parser.parse_args()

def generate_variable_store(env: dict, lab_number: str): 
    """
    Generate a variablestore entry for the purpose of creating a schematics workspace:
    """

    if lab_number == "petclinic":
        variablestore =  [
                    {
                    "name": "ibmcloud_api_key",
                    "value": env.ibmcloud_api_key,
                    "secure": True
                    },
                    {
                    "name": "ibmcloud_region",
                    "value": env.ibmcloud_region
                    },
                    {
                    "name": "director_site_name",
                    "value": env.director_site_name
                    },                    
                    {
                    "name": "director_url",
                    "value": f'{env.director_url}/api'
                    },                    
                    {
                    "name": "director_org",
                    "value": env.director_org_name
                    },                    
                    {
                    "name": "vmware_api_token",
                    "value": env.api_token,
                    "secure": True
                    },                                        
                    {
                    "name": "vdc_name",
                    "value": env.director_vdc
                    },
                    {
                    "name": "public_ip",
                    "value": env.public_ip
                    }
        ]

    return variablestore

def main() -> int:

    # parse input arguments
    args = parse_arg()

    #--------------------------------------------------------------
    # Get environment
    #--------------------------------------------------------------

    print("Processing args...")
    # Get IBM Cloud Session Token
    ibm_iam_access_token = iam.request_ibm_iam_access_token(
        ibm_api_key=args.ibmcloud_api_key
    )

    # Get director site
    print(f'Retrieving Director Site - {args.director_site_name} in region {args.ibmcloud_region}')
    director_sites = vcfass.list_director_sites(
        ibm_iam_access_token=ibm_iam_access_token, region=args.ibmcloud_region
    )['director_sites']

    site_names = [d["name"] for d in director_sites]
    if args.director_site_name not in site_names:
        print(f'Error: Site not found : {args.director_site_name}')
        exit(1)

    director_site = [d for d in director_sites if d.get('name') == args.director_site_name][0]

    # Get Director URL for the Site
    # Note: We assume we have at least 1 VDC which is always the case for multi-tenant sites

    print(f'Retrieving VDC- {args.vdc_name}')
    vdcs = vcfass.list_vcfaas_vdcs(region = args.ibmcloud_region,ibm_iam_access_token=ibm_iam_access_token)['vdcs']
    vdc =  [v for v in vdcs if v['director_site']['id'] == director_site["id"] and v['name'] == args.vdc_name][0]
    public_ip = vdc['edges'][0]['public_ips'][0]
    director_url = urlparse(vdc['director_site']['url']).scheme + "://" + urlparse(vdc['director_site']['url']).netloc
    org = vdc['org_name']
    print(f'ORG = {org}')
    print(f'Director_URL = {director_url}')

    # Get Org Id
    org_id = vcfass.get_org_id(ibm_iam_access_token, director_url, org)

    # Get Resource Group ID
    

    # Set env

    env = SimpleNamespace()

    env.schematics_lab = lab_terraform
    env.schematics_workspace = f'{schematics_catalog[env.schematics_lab]["workspace"]}-{args.ibmcloud_region}'
    env.schematics_github = f'{schematics_catalog[env.schematics_lab]["github"]}'
    env.schematics_folder = f'{schematics_catalog[env.schematics_lab]["folder"]}'
    
    env.ibmcloud_region = args.ibmcloud_region
    env.director_site_name = args.director_site_name
    env.director_url = director_url
    env.director_vdc = vdc["name"]
    env.director_org_name = vdc["org_name"]
    env.org_id = org_id
    env.director_site_id = vdc["director_site"]["id"]
    env.ibmcloud_api_key = args.ibmcloud_api_key
    env.resource_group_id = vdc['resource_group']['id']
    env.public_ip = public_ip

    print('-----------------------------------------------')
    print(f'ibmcloud_region: {env.ibmcloud_region}')
    print(f'director_site_name: {env.director_site_name}')
    print(f'director_url: {env.director_url}')
    print(f'director_vdc_vdc: {env.director_vdc}')
    print(f'director_org: {env.director_org_name}')
    print(f'director_org: {env.org_id}')
    print(f'director_site_id: {env.director_site_id}')
    print(f'resource_group_id: {env.resource_group_id}')
    print(f'schematics_workspace: {env.schematics_workspace}')
    print(f'Schematics Lab: {env.schematics_lab}')
    print(f'public_ip={env.public_ip}')
    print('-----------------------------------------------')
    
    # Get VMWare Access Token
    print(f'Retrieving VMware Access Token')
    vmware_access_token = vcfass.get_vmware_access_token(
                                ibm_iam_access_token = ibm_iam_access_token, 
                                url = env.director_url,
                                org = env.director_org_name)
    
    # Check Schematics
    print('')
    print('Checking Schematics......')
    print('--------------------------------------------------------')

    workspace = {}
    workspace_name = env.schematics_workspace
    print(f'Searching for Schematics workspace {workspace_name}')
    print('')
    workspaces = schematics.ibm_schematics_list_workspaces(ibm_iam_access_token, 'Default')
    for w in workspaces["workspaces"]:
        if w["name"] == workspace_name:
            workspace = w
    
    if workspace == {}:
         print(f'Workspace: {workspace_name} not found, will need to be created')
         action_schematics = True
    else:
        print(f'Workspace: {workspace_name} found. ')
        action_schematics = False

    # Check Catalog
    print('')
    print(f'Checking Catalog for {lab_catalog}......')
    print('--------------------------------------------------------')

    catalog_query = cloud_director.query_catalogs(director_url, vmware_access_token, filter=f'name=={lab_catalog}')
    if len(catalog_query) == 1:
        action_create_catalog = False
        print(f'Found catalog {catalog_query[0]["name"]} with a HREF of : {catalog_query[0]["href"]}')

    else:
        print(f'Catalog {lab_catalog} does not exist and needs to be created.')
        print('')
        action_create_catalog = True

    # Check if Public IP has been allocated as a FIP

    ipspaces =  cloud_director.get_ipspaces(director_url = env.director_url, 
                                            vmware_access_token = vmware_access_token)

    ipspace_id = ""
    for ipspace in ipspaces:
        ipspace_details = cloud_director.get_ipspace(director_url = env.director_url, 
                                            vmware_access_token = vmware_access_token,
                                            ipspace_id = ipspace['id'])
        if IPAddress(public_ip) in IPNetwork(ipspace_details['ipSpaceInternalScope'][0]):
            ipspace_id = ipspace_details['id']
            break
    
    if ipspace_id == "":
        print(f'Error: Expected Public IP Address {args.director_site_name} has no associated IP Space')
        exit(1)

    print(f'Determine if public IP {public_ip} has been allocated yet')
    ipspace_allocations =  cloud_director.ipspace_allocations(director_url = env.director_url, 
                                            vmware_access_token = vmware_access_token,
                                            ipspace_id = ipspace_id)
    
    if public_ip in [i['value'] for i in ipspace_allocations]:
        action_fip = False
    else:
        action_fip = True

    #--------------------------------------------------------------
    # Summary
    #--------------------------------------------------------------

    print('---------------------------------------')
    print('ACTION SUMMARY')
    print('---------------------------------------')

    print(f'CATALOG CREATE : {action_create_catalog}')
    print(f'CREATE SCHEMATICS : {action_schematics}')
    print(f'ALLOCATION PUBLIC IP : {action_fip}')


    # Manage Catalog

    print('---------------------------------------')
    print('Manage Catalog')
    print('---------------------------------------')

    if action_create_catalog:

        tasks = []
        print(f'Creating Catalog: {lab_catalog}')
        try:
            catalog = cloud_director.create_catalog(director_url = env.director_url,
                                                    vmware_access_token = vmware_access_token,
                                                    org_id = org_id,
                                                    catalog_name = lab_catalog)

            tasks.append(catalog['tasks']['task'][0]["href"])

        except Exception as e:
            print((f'Failed to create Catalog: {lab_catalog}'))
            print(e)

        print('Waiting for tasks.....')
        cloud_director.wait_for_tasks(
                vmware_access_token=vmware_access_token,
                tasks=tasks)
    else:
        print("Nothing to do...")

    # Manage Schematics

    print('---------------------------------------')
    print('Manage Schematics')
    print('---------------------------------------')

    if action_schematics:

        token_name = f'TOKEN-{uuid.uuid4()}'
        print(f'Creating API Token {token_name}')
        env.api_token = cloud_director.create_apitoken(director_url, vmware_access_token, env.director_org_name,  org_id, token_name)

        print(f'Creating Scheamtics Workspace: {env.schematics_workspace}')
        try:
            s = schematics.ibm_schematics_create_workspace(ibm_iam_access_token = ibm_iam_access_token,
                                                            resource_group =  env.resource_group_id,
                                                            workspace_name = f'{env.schematics_workspace}',
                                                            description = 'Created by automation',
                                                            template_repo = env.schematics_github,
                                                            folder = env.schematics_folder,
                                                            type = 'terraform_v1.6',
                                                            variablestore = generate_variable_store(env, env.schematics_lab))
            print('Worspace creation successful, please visit https://cloud.ibm.com/schematics/workspaces.')

        except Exception as e:
            print((f'Failed to create workspace: {env.schematics_workspace}'))
            print(e)

        print('---------------------------------------')
        print('Terrfaform Variables')
        print('---------------------------------------')

        print(f'ibmcloud_api_key="{env.ibmcloud_api_key}"')
        print(f'ibmcloud_region="{env.ibmcloud_region}"')
        print(f'director_site_name="{env.director_site_name}"')
        print(f'director_url="{env.director_url}/api"')
        print(f'director_org_name="{env.director_org_name}"')
        print(f'vmware_api_token="{env.api_token}"')
        print(f'director_vdc="{env.director_vdc}"')
        print(f'public_ip="{env.public_ip}"')

    else:
        print("Nothing to do...")

    # Managed Public IP
    print('---------------------------------------')
    print('Manage Public IP')
    print('---------------------------------------')

    if action_fip:

        print('Allocating Public IP Address as FIP')
        task = cloud_director.ipspaces_allocate_ip(director_url = env.director_url,
                                    vmware_access_token = vmware_access_token,
                                    ipspace_id = ipspace_id)

if __name__ == "__main__":
    exit(main())
