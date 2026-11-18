mock_provider "azurerm" {}

variables {
  name                = "lab-dev-vnet"
  location            = "usgovvirginia"
  resource_group_name = "rg-lab-dev"
  address_space       = "10.10.0.0/16"
  subnets = {
    apps = {
      prefix = "10.10.0.0/24"
      allow_rules = [
        { name = "allow-https-from-vnet", priority = 100, protocol = "Tcp", port = "443", source = "VirtualNetwork" }
      ]
    }
    data = { prefix = "10.10.1.0/24" }
  }
}

run "every_subnet_gets_a_deny_all_nsg" {
  command = plan

  assert {
    condition     = length(azurerm_network_security_group.this) == 2
    error_message = "expected one NSG per subnet"
  }

  assert {
    condition = alltrue([
      for k, nsg in azurerm_network_security_group.this :
      anytrue([for r in nsg.security_rule : r.name == "deny-all-inbound" && r.access == "Deny" && r.priority == 4096])
    ])
    error_message = "every NSG must end with deny-all-inbound"
  }

  assert {
    condition     = length(azurerm_subnet_network_security_group_association.this) == 2
    error_message = "every subnet must be associated with its NSG"
  }
}

run "bad_cidr_is_rejected" {
  command = plan

  variables {
    address_space = "10.10.0.0/99"
  }

  expect_failures = [var.address_space]
}
