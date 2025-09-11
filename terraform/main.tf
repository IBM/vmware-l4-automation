################################################################################
# Data Variables
################################################################################3wes

data "vcd_catalog" "lab-catalog" {
  org  = var.director_org
  name = var.catalog
}

data "vcd_catalog_vapp_template" "vm_template" {
  org        = var.director_org
  catalog_id = data.vcd_catalog.lab-catalog.id
  name       = var.virtual_machine.template_name
}

################################################################################
# Deploy Virtual Machine
################################################################################

resource "vcd_vm" "virtual_machine" {
  name = var.virtual_machine.name
  vapp_template_id  = data.vcd_catalog_vapp_template.vm_template.id
  memory = var.virtual_machine.memory
  cpus = var.virtual_machine.cpus
  power_on = var.virtual_machine.power_on
  vdc = var.director_vdc

  network {
      type = var.virtual_machine.network.type
      name = var.virtual_machine.network.name
      ip_allocation_mode = var.virtual_machine.network.ip_allocation_mode
      ip = var.virtual_machine.network.ip
      is_primary = var.virtual_machine.network.is_primary
  }
}