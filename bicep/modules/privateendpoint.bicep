@description('Private endpoint for one resource, with DNS registered in a private zone.')
param name string
param location string = resourceGroup().location
param subnetId string
param targetResourceId string

@description('Sub-resource, for example blob, vault, sqlServer.')
param groupId string
param privateDnsZoneId string

resource pe 'Microsoft.Network/privateEndpoints@2024-03-01' = {
  name: name
  location: location
  properties: {
    subnet: {
      id: subnetId
    }
    privateLinkServiceConnections: [
      {
        name: name
        properties: {
          privateLinkServiceId: targetResourceId
          groupIds: [groupId]
        }
      }
    ]
  }
}

resource zoneGroup 'Microsoft.Network/privateEndpoints/privateDnsZoneGroups@2024-03-01' = {
  parent: pe
  name: 'default'
  properties: {
    privateDnsZoneConfigs: [
      {
        name: 'config'
        properties: {
          privateDnsZoneId: privateDnsZoneId
        }
      }
    ]
  }
}

output id string = pe.id
