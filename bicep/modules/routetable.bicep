@description('Route table that sends all outbound traffic through the firewall.')
param name string
param location string = resourceGroup().location

@description('Private IP of the firewall or virtual appliance.')
param firewallPrivateIp string

resource rt 'Microsoft.Network/routeTables@2024-03-01' = {
  name: name
  location: location
  properties: {
    disableBgpRoutePropagation: true
    routes: [
      {
        name: 'default-via-firewall'
        properties: {
          addressPrefix: '0.0.0.0/0'
          nextHopType: 'VirtualAppliance'
          nextHopIpAddress: firewallPrivateIp
        }
      }
    ]
  }
}

output id string = rt.id
