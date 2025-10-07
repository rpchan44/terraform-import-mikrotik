resource "routeros_interface_ethernet" "ether1" {
  name     = "ether1"
  mtu      = 1500
  mac_address = "08:55:31:5F:84:FE"
  disabled = false
}

resource "routeros_interface_ethernet" "ether2" {
  name     = "ether2"
  mtu      = 1500
  mac_address = "08:55:31:5F:84:FF"
  disabled = false
}

resource "routeros_interface_ethernet" "ether3" {
  name     = "ether3"
  mtu      = 1500
  mac_address = "08:55:31:5F:85:00"
  disabled = false
}

resource "routeros_interface_ethernet" "ether4" {
  name     = "ether4"
  mtu      = 1500
  mac_address = "08:55:31:5F:85:01"
  disabled = false
}

resource "routeros_interface_ethernet" "ether5" {
  name     = "ether5"
  mtu      = 1500
  mac_address = "08:55:31:5F:85:02"
  disabled = false
}

resource "routeros_interface" "wlan1" {
  name     = "wlan1"
  mtu      = 1500
  mac_address = "08:55:31:5F:85:03"
  disabled = false
}

resource "routeros_interface" "wlan2" {
  name     = "wlan2"
  mtu      = 1500
  mac_address = "08:55:31:5F:85:04"
  disabled = false
}

resource "routeros_interface_vlan" "IOT/CCTV" {
  name     = "IOT/CCTV"
  mtu      = 1500
  mac_address = "08:55:31:5F:85:04"
  disabled = false
}

resource "routeros_interface_bridge" "Management" {
  name     = "Management"
  mtu      = auto
  mac_address = "08:55:31:5F:85:04"
  disabled = false
}

resource "routeros_interface_vlan" "Proxmox" {
  name     = "Proxmox"
  mtu      = 1500
  mac_address = "08:55:31:5F:85:04"
  disabled = false
}

resource "routeros_interface_vlan" "Server" {
  name     = "Server"
  mtu      = 1500
  mac_address = "08:55:31:5F:85:04"
  disabled = false
}

resource "routeros_interface_vlan" "Storage" {
  name     = "Storage"
  mtu      = 1500
  mac_address = "08:55:31:5F:85:04"
  disabled = false
}

resource "routeros_interface" "VPN_>CN" {
  name     = "VPN->CN"
  disabled = true
}

resource "routeros_interface" "VPN_>EMD" {
  name     = "VPN->EMD"
  mtu      = 1500
  disabled = false
}

resource "routeros_interface" "VPN_>JJ" {
  name     = "VPN->JJ"
  mtu      = 1500
  disabled = false
}

resource "routeros_interface" "VPN_>LC" {
  name     = "VPN->LC"
  mtu      = 1420
  disabled = false
}

resource "routeros_interface" "VPN_>Z1" {
  name     = "VPN->Z1"
  mtu      = 1500
  disabled = false
}

resource "routeros_interface" "VPN_VX" {
  name     = "VPN-VX"
  mtu      = 1500
  disabled = false
  comment  = "222.127.208.224 ; 222.127.154.216 ; 222.127.152.132"
}

resource "routeros_interface" "back_to_home_vpn" {
  name     = "back-to-home-vpn"
  mtu      = 1420
  disabled = false
  comment  = "back-to-home-vpn"
}

resource "routeros_interface" "lo" {
  name     = "lo"
  mtu      = 65536
  mac_address = "00:00:00:00:00:00"
  disabled = false
}

