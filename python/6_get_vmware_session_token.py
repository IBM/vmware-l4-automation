import argparse
import os
import json
import re
import uuid

import lib.iam as iam
import lib.vcfaas as vcfass
from urllib.parse import urlparse


def parse_arg() -> argparse.Namespace:
    """Parse input arguments.

    Returns:
        argparse object with parsed arguments.
    """

    parser = argparse.ArgumentParser(prog=os.path.basename(__file__))
    parser.add_argument("-k", dest="ibmcloud_api_key", help="IBM Cloud API Key", required=True)
    parser.add_argument("-u", dest="director_url", help="Cloud Director URL", required=True)
    parser.add_argument("-o", dest="director_org", help="Cloud Director ORG", required=True)


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
    # Get VMWare Access Token
    #--------------------------------------------------------------
    print("Getting VMware Access Token....")
    vmware_access_token = vcfass.get_vmware_access_token(
                                ibm_iam_access_token = ibm_iam_access_token, 
                                url = args.director_url,
                                org = args.director_org)

    print("")
    print(f'VMware Access Token : {vmware_access_token}')

if __name__ == "__main__":
    exit(main())
