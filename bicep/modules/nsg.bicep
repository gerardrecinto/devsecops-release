@description('Network security group name.')
param name string
param location string = resourceGroup().location

@description('Allow rules. Everything else inbound is denied by the last rule.')
param allowRules array = []

var denyAll = {
  name: 'deny-all-inbound'
  properties: {
    priority: 4096
    direction: 'Inbound'
    access: 'Deny'
    protocol: '*'
    sourcePortRange: '*'
    destinationPortRange: '*'
    sourceAddressPrefix: '*'
    destinationAddressPrefix: '*'
  }
}

resource nsg 'Microsoft.Network/networkSecurityGroups@2024-03-01' = {
  name: name
  location: location
  properties: {
    securityRules: concat(allowRules, [denyAll])
  }
}

output id string = nsg.id
