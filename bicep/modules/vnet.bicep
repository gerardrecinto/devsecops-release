@description('Virtual network name.')
param name string
param location string = resourceGroup().location
param addressPrefix string

@description('Subnets: name, prefix, optional nsgId and routeTableId.')
param subnets array

resource vnet 'Microsoft.Network/virtualNetworks@2024-03-01' = {
  name: name
  location: location
  properties: {
    addressSpace: {
      addressPrefixes: [addressPrefix]
    }
    subnets: [for s in subnets: {
      name: s.name
      properties: {
        addressPrefix: s.prefix
        networkSecurityGroup: contains(s, 'nsgId') ? { id: s.nsgId } : null
        routeTable: contains(s, 'routeTableId') ? { id: s.routeTableId } : null
        privateEndpointNetworkPolicies: 'Enabled'
      }
    }]
  }
}

output id string = vnet.id
output subnetIds object = toObject(vnet.properties.subnets, s => s.name, s => s.id)
