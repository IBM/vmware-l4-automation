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

  description = "The name of the director site, for example IBM VCFaaS Multitenant - WDC"
  default = ""

}

variable "director_url" {

  description = "The access URL for the Site, example: https://dirw003.us-east.vmware.cloud.ibm.com/api"
  default = ""

}

variable "director_org_name" {

  description = "The Director Organization Name, example: 2c01737d-ee41-4011-8819-99e7efa8d20c"
  default = ""

}

variable "vmware_api_token" {

  description = "VMWare API Token for VCD"
  default = ""

}

##############################################################################
# VDC Variables
##############################################################################

variable "director_vdc" {

    description = "Name of the Virtual Data Center"
    default = ""
}

variable "public_ip" {

    description = "The public IP address to be used to access the petstore application"
    default = ""
}

variable "dns_servers" {
  default = ["161.26.0.10","161.26.0.11"] 
}

variable "dns_suffix" {
  default = "vcf.lab"
}
variable "vdc_networks" {

  description = "Network template for the APP network" 
  default = {
    lab-web = {
      description = "Lab Web Network"
      type = "routed"
      subnet = {
        cidr = "192.168.100.9/29"
        prefix_length = 29
        gateway = "192.168.100.9"
        static_ip_pool = {
          start_address = "192.168.100.10"
          end_address   = "192.168.100.14"
        }       
      }
    },
    lab-app = {
      description = "Lab Application Network"
      type = "routed"
      subnet = {
        cidr = "192.168.101.9/29"
        prefix_length = 29
        gateway = "192.168.101.9"
        static_ip_pool = {
          start_address = "192.168.101.10"
          end_address   = "192.168.101.14"
        }       
      }
    }
  }
}

##############################################################################
# Virtual Machine Variables
##############################################################################

variable "catalog" {
    description = "The name of the catalog the vApp templates reside in"
    default = "PetClinic"
}

variable "virtual_machines" {
  description = "Virtual Machine types to create for each VDC"
  default = {
    lab01-web = {
      template_name = "ibm-vcfaas-lab-apache2"
      power_on = true
      network = {
        name = "lab-web"
        type = "org"
        ip_allocation_mode = "MANUAL"
        ip = "192.168.100.10"
        is_primary = true
      }
      memory = 2048
      cpus = 2
    },
    lab01-app = {
      template_name = "ibm-vcfaas-lab-tomcat"
      power_on = false
      network = {
        name = "lab-app"
        type = "org"
        ip_allocation_mode = "MANUAL"
        ip = "192.168.101.10"
        is_primary = true
      }
      memory = 2048
      cpus = 2
    },
    lab01-data = {
      template_name = "ibm-vcfaas-lab-mysql"
      power_on = true
      network = {
        name = "lab-app"
        type = "org"
        ip_allocation_mode = "MANUAL"
        ip = "192.168.101.11"
        is_primary = true
      }
      memory = 2048
      cpus = 2
    }
  }
}

##############################################################################
# SNAT and DNAT Variables
##############################################################################

variable "dnat" {
  description = "DNAT rules"
  default = {
    public-petclinic = {
      description = "Public access to petclinic web server"
      internal_address = "192.168.100.10"
      dnat_external_port = "80"
    }
  }
}

variable "snat" {
  description = "SNAT rules"
  default = {
    web-public = {
      description = "Outgoing access from the web server to the internet"
      internal_address = "192.168.100.10"
    }
  }
}

##############################################################################
# Security Variables - IP Sets and FW Rules
##############################################################################

variable "ip_sets" {
  description = "DNAT rules"
  default = {
    web-servers = {
      description = "Web Servers IP Set"
      ip_addresses = ["192.168.100.10"]
    }
  }
}

variable "all_port_profiles" {
  description = "A list of all Port Profiles used in the firewall rule section."
  default = ["HTTP", "HTTPS", "DNS-TCP", "DNS IN", "ICMP ALL"]
}

variable "firewall_rules" {
  description = "Lab firewall rules"
  default = {
    public-web = {
      direction = "IN"
      ip_protocol = "IPV4"
      action = "ALLOW"
      enabled = true
      logging = true
      source = []
      destination = ["web-servers"]
      app_port_profile = ["HTTP"]
    },
    web-public = {
      direction = "OUT"
      ip_protocol = "IPV4"
      action = "ALLOW"
      enabled = true
      logging = true
      source = ["web-servers"]
      destination = []
      app_port_profile = ["HTTP", "HTTPS", "DNS-TCP", "DNS IN", "ICMP ALL"]
    }
  }
}