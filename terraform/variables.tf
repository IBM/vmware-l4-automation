##############################################################################
# Provider Variables
##############################################################################

variable "ibmcloud_api_key" {
  description = "Enter the IBM Cloud API Key"
}

variable "ibmcloud_region" {

  description = "Region the defined transit gateway exists in"
  default = ""

}

##############################################################################
# Director Site Variables
##############################################################################

variable "director_site_name" {

  description = "The name of the director site, for example IBM VCFaaS Multitenant - DAL"
  default = ""

}

variable "director_url" {

  description = "The access URL for the Site, example: https://dirw003.us-east.vmware.cloud.ibm.com/api"
  default = ""

}

variable "director_org" {

  description = "The Director Organization ID, example: 2c01737d-ee41-4011-8819-99e7efa8d20c"
  default = ""

}

variable "director_vdc" {

  description = "The name of the Virtual Data Center to deploy Virtual Machines"
  default = ""

}

variable "vmware_api_token" {

  description = "VMWare API Token for VCD"
  default = ""

}

##############################################################################
# Virtual Machine Variables
##############################################################################

variable "catalog" {
    description = "The name of the catalog the vApp templates reside in"
    default = "PetClinic"
}

variable "virtual_machine" {
  description = "Virtual Machine to create for the Automation lab"
  default = {
    name = "sample_vm_apache"
    template_name = "ibm-vcfaas-lab-apache2"
    power_on = false
    network = {
        name = "lab-web"
        type = "org"
        ip_allocation_mode = "MANUAL"
        ip = "192.168.100.12"
        is_primary = true
        dns_suffix = "vcf.lab"
        dns_servers = ["161.26.0.10","161.26.0.11"] 
    }
    memory = 2048
    cpus = 2
  }
}
