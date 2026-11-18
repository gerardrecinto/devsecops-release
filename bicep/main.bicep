targetScope = 'resourceGroup'

@allowed(['dev', 'test', 'staging', 'prod'])
param env string
param location string = resourceGroup().location
param addressPrefix string
param firewallPrivateIp string

var prefix = 'lab-${env}'

module nsgApps 'modules/nsg.bicep' = {
  name: 'nsg-apps'
  params: {
    name: '${prefix}-apps-nsg'
    location: location
    allowRules: [
      {
        name: 'allow-https-from-vnet'
        properties: {
          priority: 100
          direction: 'Inbound'
          access: 'Allow'
          protocol: 'Tcp'
          sourcePortRange: '*'
          destinationPortRange: '443'
          sourceAddressPrefix: 'VirtualNetwork'
          destinationAddressPrefix: '*'
        }
      }
    ]
  }
}

module nsgData 'modules/nsg.bicep' = {
  name: 'nsg-data'
  params: {
    name: '${prefix}-data-nsg'
    location: location
  }
}

module rt 'modules/routetable.bicep' = {
  name: 'route-table'
  params: {
    name: '${prefix}-rt'
    location: location
    firewallPrivateIp: firewallPrivateIp
  }
}

module vnet 'modules/vnet.bicep' = {
  name: 'vnet'
  params: {
    name: '${prefix}-vnet'
    location: location
    addressPrefix: addressPrefix
    subnets: [
      { name: 'snet-apps', prefix: cidrSubnet(addressPrefix, 24, 0), nsgId: nsgApps.outputs.id, routeTableId: rt.outputs.id }
      { name: 'snet-data', prefix: cidrSubnet(addressPrefix, 24, 1), nsgId: nsgData.outputs.id, routeTableId: rt.outputs.id }
      { name: 'snet-pe', prefix: cidrSubnet(addressPrefix, 24, 2), nsgId: nsgData.outputs.id }
    ]
  }
}

resource storage 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: 'st${uniqueString(resourceGroup().id, env)}'
  location: location
  kind: 'StorageV2'
  sku: {
    name: 'Standard_GRS'
  }
  properties: {
    minimumTlsVersion: 'TLS1_2'
    allowBlobPublicAccess: false
    allowSharedKeyAccess: false
    supportsHttpsTrafficOnly: true
    publicNetworkAccess: 'Disabled'
    networkAcls: {
      defaultAction: 'Deny'
      bypass: 'AzureServices'
    }
  }
}

module blobZone 'modules/privatednszone.bicep' = {
  name: 'blob-zone'
  params: {
    zoneName: 'privatelink.blob.${environment().suffixes.storage}'
    vnetId: vnet.outputs.id
  }
}

module blobEndpoint 'modules/privateendpoint.bicep' = {
  name: 'blob-endpoint'
  params: {
    name: '${prefix}-blob-pe'
    location: location
    subnetId: vnet.outputs.subnetIds['snet-pe']
    targetResourceId: storage.id
    groupId: 'blob'
    privateDnsZoneId: blobZone.outputs.id
  }
}

output vnetId string = vnet.outputs.id
