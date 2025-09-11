import argparse
import os
import json
import re
import uuid

import lib.iam as iam
import lib.vcfaas as vcfass

def parse_arg() -> argparse.Namespace:
    """Parse input arguments.

    Returns:
        argparse object with parsed arguments.
    """

    parser = argparse.ArgumentParser(prog=os.path.basename(__file__))
    parser.add_argument("-k", dest="ibmcloud_api_key", help="IBM Cloud API Key", required=True)
    parser.add_argument("-r", dest="ibmcloud_region", help="IBM Cloud Region", required=True)
    parser.add_argument("-s", dest="director_site_name", help="Cloud Director Site Name", required=True)
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

    director_site_names = [d["name"] for d in director_sites]
    if args.director_site_name not in director_site_names:
        print(f'Error: Site not found : {args.director_site_name}')
        exit(1)

    #--------------------------------------------------------------
    # Extract director site id
    #--------------------------------------------------------------

    director_site_id = [d for d in director_sites if d.get('name') == args.director_site_name][0]['id']

    #--------------------------------------------------------------
    # Get Director Site
    #--------------------------------------------------------------

    director_site = vcfass.get_director_site(
        ibm_iam_access_token = ibm_iam_access_token, 
        region = args.ibmcloud_region,
        site_id = director_site_id
    )

    print("")
    pretty_director_site = json.dumps(director_site, indent=4)
    print(pretty_director_site)

if __name__ == "__main__":
    exit(main())
