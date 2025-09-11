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
    # List Virtual Data Centres
    #--------------------------------------------------------------
    print("Listing Virtual Data Centers")
    vdcs = vcfass.list_vcfaas_vdcs(
        ibm_iam_access_token=ibm_iam_access_token, 
        region=args.ibmcloud_region
    )['vdcs']

    print("")
    pretty_vdcs = json.dumps(vdcs, indent=4)
    print(pretty_vdcs)


if __name__ == "__main__":
    exit(main())
