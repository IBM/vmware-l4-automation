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

schematics_catalog = {
    "petclinic" : {"folder": "petclinic",
          "github": "https://github.com/IBM/vmware-l4-automation.git",
          "workspace" : "petclinic"}
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
    print('-----------------------------------------------')
    
    # Get VMWare Access Token
    print(f'Retrieving VMware Access Token')
    vmware_access_token = vcfass.get_vmware_access_token(
                                ibm_iam_access_token = ibm_iam_access_token, 
                                url = env.director_url,
                                org = env.director_org_name)

    # Check Catalog
    print('')
    print(f'Checking Catalog for {lab_catalog}......')
    print('--------------------------------------------------------')

    action_create_catalog = False
    missing_catalog_items = catalog_items
    catalog_query = cloud_director.query_catalogs(director_url, vmware_access_token, filter=f'name=={lab_catalog}')
    if len(catalog_query) == 1:
        print(f'Found catalog {catalog_query[0]["name"]} with a HREF of : {catalog_query[0]["href"]}')
        print(f'Retreiving Catalog Items....')
        catalog = cloud_director.get_resource(vmware_access_token, catalog_query[0]["href"])
        for catalog_item in catalog["catalogItems"]["catalogItem"]:
             print(f'    - {catalog_item["name"]}')
             if catalog_item["name"] in missing_catalog_items:
                  missing_catalog_items.remove(catalog_item["name"])

    else:
        action_create_catalog = True

    print('')
    if action_create_catalog:
         print(f'Catalog {lab_catalog} does not exist and needs to be created.')
         print('')
    else:
         print(f'Catalog {lab_catalog} exists and does NOT to be created.')
         print('')

    if len(missing_catalog_items) == 0:
         print('All catalog items up to date, nothing to do...')
    else:
         print('The following catalog items need to be created:')
         for item in missing_catalog_items:
              print(f'    - {item}')

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
        
    if len(missing_catalog_items) > 0:
        
        print(f'Uploading {len(missing_catalog_items)} Catalog Items')
        for catalog_item in missing_catalog_items:
                
            try:
                print(f'    Uploading {catalog_item}: {lab_catalog_items[catalog_item]}')
                catalog_item = cloud_director.upload_ovf(director_url = env.director_url,
                                                        vmware_access_token = vmware_access_token,
                                                        catalog_id = catalog['id'].split(':')[-1],
                                                        ovf_url = lab_catalog_items[catalog_item],
                                                        item_name = catalog_item)

            except Exception as e:
                print((f'Failed to Upload Catalog Item: {catalog_item}'))
                print(e)

    else:
            print('Catalog Items up to date, nothing to do!!!')

if __name__ == "__main__":
    exit(main())
