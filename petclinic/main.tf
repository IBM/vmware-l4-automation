################################################################################
# Data Variables
################################################################################

data "vcd_resource_list" "list_of_vdcs" {
  name =  "list_of_vdcs"
  resource_type = "vcd_org_vdc"
  list_mode = "name"
}

data "vcd_resource_list" "list_of_vdc_edges" {
  for_each = {for v in data.vcd_resource_list.list_of_vdcs.list: v => v}
  name =  "list_of_vdc_edges"
  resource_type = "vcd_nsxt_edgegateway"
  list_mode = "name"
  vdc = each.value
}


data "vcd_org_vdc" "org_vdc" {
  for_each = {for v in data.vcd_resource_list.list_of_vdcs.list: v => v}
  name = each.value
}

data "vcd_nsxt_edgegateway" "edges" {
  for_each = {for k, v in data.vcd_resource_list.list_of_vdc_edges: v.vdc => v if length(v.list) > 0}
  name = each.value.list[0]
  owner_id = data.vcd_org_vdc.org_vdc[each.value.vdc].id
}

data "vcd_catalog" "lab-catalog" {
  org  = var.director_org_name
  name = var.catalog
}

data "vcd_resource_list" "vcd_catalog_vapp_template" {
  name               = "list_of_catalogs"
  resource_type      = "vcd_catalog_vapp_template"
  list_mode          = "name"
  parent             = var.catalog
}

data "vcd_catalog_vapp_template" "list_of_vapp_template" {
  for_each = {for v in data.vcd_resource_list.vcd_catalog_vapp_template.list: v => v}
  org        = var.director_org_name
  catalog_id = data.vcd_catalog.lab-catalog.id
  name       = each.value
}

data "vcd_nsxt_app_port_profile" "system" {
  for_each =  {for v in var.all_port_profiles: v => v}
  scope = "SYSTEM"
  name = each.key
}

################################################################################
# Create Networks
################################################################################

locals {
  lab_networks = flatten([
      for k, v in var.vdc_networks:  {
        name = "${k}"
        description = v.description
        edge_gateway_id = data.vcd_resource_list.list_of_vdc_edges["${var.director_vdc}"].list[0]
        gateway = v.subnet.gateway
        prefix_length = v.subnet.prefix_length
        start_address = v.subnet.static_ip_pool.start_address
        end_address = v.subnet.static_ip_pool.end_address
        vdc = "${var.director_vdc}"
      }
  ])
}

resource "vcd_network_routed_v2" "vdc_networks" {
  for_each = {for v in local.lab_networks: v.name => v}

  name            = each.key
  description     = each.value.description

  edge_gateway_id = data.vcd_nsxt_edgegateway.edges[each.value.vdc].id
  gateway         = each.value.gateway
  prefix_length   = each.value.prefix_length

  static_ip_pool {
    start_address = each.value.start_address
    end_address   = each.value.end_address
  }

  dns1            = var.dns_servers[0]
  dns2            = var.dns_servers[1]

  dns_suffix      = var.dns_suffix
}

################################################################################
# Deploy Virtual Machines
################################################################################

locals {
  lab_virtual_machines = flatten([
      for k, v in var.virtual_machines:  {
        vm_id = "${k}"
        name = "${k}"
        computer_name = k
        template_name = v.template_name
        memory = v.memory
        cpus = v.cpus
        power_on = v.power_on
        vdc = "${var.director_vdc}"
        network = {
          name = vcd_network_routed_v2.vdc_networks["${v.network.name}"].name
          type = v.network.type
          ip_allocation_mode = v.network.ip_allocation_mode
          ip = v.network.ip
          is_primary = v.network.is_primary
        }
      }
  ])
}

resource "vcd_vm" "virtual_machines" {
  for_each = {for v in local.lab_virtual_machines: v.vm_id => v}
  name = each.value.name
  vapp_template_id  = data.vcd_catalog_vapp_template.list_of_vapp_template[each.value.template_name].id
  memory = each.value.memory
  cpus = each.value.cpus
  power_on = each.value.power_on
  vdc = each.value.vdc

  network {
      type = each.value.network.type
      name = each.value.network.name
      ip_allocation_mode = each.value.network.ip_allocation_mode
      ip = each.value.network.ip
      is_primary = each.value.network.is_primary
  }
}

################################################################################
# Create SNAT / DNAT Rules
################################################################################

locals {
  dnat = flatten([
      for k, v in var.dnat:  {
        name = k
        dnat_id = "${k}"
        description = v.description
        org = var.director_org_name
        edge_gateway_id = data.vcd_nsxt_edgegateway.edges["${var.director_vdc}"].id
        external_address = var.public_ip
        internal_address = v.internal_address
        dnat_external_port = v.dnat_external_port
      }
  ])

  snat = flatten([
      for k, v in var.snat:  {
        name = k
        snat_id = "${k}"
        description = v.description
        org = var.director_org_name
        edge_gateway_id = data.vcd_nsxt_edgegateway.edges["${var.director_vdc}"].id
        external_address = var.public_ip
        internal_address = v.internal_address
      }
  ])
}

resource "vcd_nsxt_nat_rule" "dnat" {
  for_each = {for v in local.dnat: v.dnat_id => v}

  name = each.value.name
  description = each.value.description
  org = each.value.org
  edge_gateway_id = each.value.edge_gateway_id
  rule_type   = "DNAT"
  external_address = each.value.external_address
  internal_address = each.value.internal_address
  dnat_external_port = each.value.dnat_external_port
  logging = true
}

resource "vcd_nsxt_nat_rule" "snat" {
  for_each = {for v in local.snat: v.snat_id => v}

  name             = each.value.name
  description      = each.value.description
  org              = each.value.org
  edge_gateway_id  = each.value.edge_gateway_id
  rule_type        = "SNAT"
  external_address = each.value.external_address
  internal_address = each.value.internal_address
  logging          = true
}

################################################################################
# IP Sets
################################################################################

locals {
  ip_sets = flatten([
      for k, v in var.ip_sets:  {
        name = k
        set_id = "${k}"
        description = v.description
        org = var.director_org_name
        edge_gateway_id = data.vcd_nsxt_edgegateway.edges["${var.director_vdc}"].id
        ip_addresses = v.ip_addresses
      }
  ])
}

resource "vcd_nsxt_ip_set" "ip_set" {
  for_each = {for v in local.ip_sets: v.set_id => v}

  org                      = each.value.org
  edge_gateway_id          = each.value.edge_gateway_id
  name                     = each.value.name
  description              = each.value.description
  ip_addresses             = each.value.ip_addresses
}

################################################################################
# Firewall Rules
################################################################################

resource "vcd_nsxt_firewall" "firewall" {
  org = var.director_org_name
  edge_gateway_id = data.vcd_nsxt_edgegateway.edges["${var.director_vdc}"].id

  dynamic "rule" {
    for_each = var.firewall_rules
    content {
      action               = rule.value.action
      name                 = rule.key
      enabled              = rule.value.enabled
      direction            = rule.value.direction
      ip_protocol          = rule.value.ip_protocol
      source_ids           = [for v in rule.value.source : vcd_nsxt_ip_set.ip_set["${v}"].id]
      destination_ids      = [for v in rule.value.destination : vcd_nsxt_ip_set.ip_set["${v}"].id]
      app_port_profile_ids = [for v in rule.value.app_port_profile : data.vcd_nsxt_app_port_profile.system["${v}"].id]
      logging              = rule.value.logging
    }
  }

  depends_on = [
    vcd_nsxt_ip_set.ip_set
  ]
}