import argparse
import os
import json
import re
import uuid

import lib.iam as iam
import lib.vcfaas as vcfass
import lib.cloud_director as cloud_director

from urllib.parse import urlparse


def parse_arg() -> argparse.Namespace:
    """Parse input arguments.

    Returns:
        argparse object with parsed arguments.
    """

    parser = argparse.ArgumentParser(prog=os.path.basename(__file__))
    parser.add_argument("-k", dest="ibmcloud_api_key", help="IBM Cloud API Key", required=True)
    parser.add_argument("-r", dest="ibmcloud_region", help="IBM Cloud Region", required=True)
    parser.add_argument("-s", dest="director_site_name", help="Cloud Director Site Name", required=True)
    parser.add_argument("-v", dest="vdc_name", help="Virtual Data Center Name", required=True)

    return parser.parse_args()

def main() -> int:

    # parse input arguments
    print("Processing args...")
    args = parse_arg()

    #--------------------------------------------------------------
    # Get Session Token
    #--------------------------------------------------------------

    print("Getting Access Token....")
    # Get IBM Cloud Session Token
    ibm_iam_access_token = iam.request_ibm_iam_access_token(
        ibm_api_key=args.ibmcloud_api_key
    )

    #--------------------------------------------------------------
    # List Director Sites
    #--------------------------------------------------------------

    print("Getting Director Sites....")
    director_sites = vcfass.list_director_sites(
        ibm_iam_access_token=ibm_iam_access_token, 
        region=args.ibmcloud_region
    )['director_sites']

    #--------------------------------------------------------------
    # Extract director site id
    #--------------------------------------------------------------

    director_site_id = [d for d in director_sites if d.get('name') == args.director_site_name][0]['id']

    #--------------------------------------------------------------
    # List Virtual Data Centres
    #--------------------------------------------------------------
    print("Listing Virtual Data Centers")
    vdcs = vcfass.list_vcfaas_vdcs(
        ibm_iam_access_token=ibm_iam_access_token, 
        region=args.ibmcloud_region
    )['vdcs']

    #--------------------------------------------------------------
    # Get VDC based on vdc_name
    #--------------------------------------------------------------

    vdc =  [v for v in vdcs if v['director_site']['id'] == director_site_id][0]

    #--------------------------------------------------------------
    # Extract VMware Director URL and ORG 
    #--------------------------------------------------------------

    director_url = urlparse(vdc['director_site']['url']).scheme + "://" + urlparse(vdc['director_site']['url']).netloc
    org_name = vdc['org_name']

    #--------------------------------------------------------------
    # Get VMWare Access Token
    #--------------------------------------------------------------
    print("Getting VMware Access Token....")
    vmware_access_token = vcfass.get_vmware_access_token(
                                ibm_iam_access_token = ibm_iam_access_token, 
                                url = director_url,
                                org = org_name)

    #--------------------------------------------------------------
    # Get VMWare Access Token
    #--------------------------------------------------------------
    org_id = vcfass.get_org_id(ibm_iam_access_token, director_url, org_name)

    #--------------------------------------------------------------
    # Get VMWare Access Token
    #--------------------------------------------------------------

    token_name = f'TOKEN-{uuid.uuid4()}'
    print("Getting VMware API Key....")
    vmware_api_token = cloud_director.create_apitoken(director_url, vmware_access_token, org_name,  org_id, token_name)


    print("")
    print(f'ibmcloud_region = {args.ibmcloud_region}')
    print(f'director_site_name = {args.director_site_name}')
    print(f'director_url = {director_url}/api')
    print(f'director_org = {org_name}')
    print(f'director_vdc = {args.vdc_name}')
    print(f'vmware_api_token = {vmware_api_token}')
    print(f'ibmcloud_api_key = {args.ibmcloud_api_key}')

if __name__ == "__main__":
    exit(main())
