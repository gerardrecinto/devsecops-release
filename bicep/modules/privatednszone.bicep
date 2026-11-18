@description('Private DNS zone linked to a virtual network.')
param zoneName string
param vnetId string

resource zone 'Microsoft.Network/privateDnsZones@2024-06-01' = {
  name: zoneName
  location: 'global'
}

resource link 'Microsoft.Network/privateDnsZones/virtualNetworkLinks@2024-06-01' = {
  parent: zone
  name: 'link-${uniqueString(vnetId)}'
  location: 'global'
  properties: {
    virtualNetwork: {
      id: vnetId
    }
    registrationEnabled: false
  }
}

output id string = zone.id
