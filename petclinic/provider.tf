##############################################################################
# Terraform Providers
##############################################################################

terraform {
  required_providers {
    random = {
      source  = "hashicorp/random"
      version = "3.5.1"
    }
    vcd = {
      source = "vmware/vcd"
    }  
  }
}

##############################################################################
# VCD Provider
##############################################################################

provider "vcd" {

  user                 = "none"
  password             = "none"
  auth_type            = "api_token"
  api_token            = var.vmware_api_token
  org                  = var.director_org_name
  vdc                  = var.director_vdc
  url                  = var.director_url

}