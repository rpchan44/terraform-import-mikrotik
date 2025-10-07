resource "routeros_interface_bridge_port" "Management_ether2" {
  interface = "ether2"
  bridge    = "Management"
  disabled  = false
  priority  = 0x80
}

resource "routeros_interface_bridge_port" "Management_wlan1" {
  interface = "wlan1"
  bridge    = "Management"
  disabled  = false
  priority  = 0x80
}

resource "routeros_interface_bridge_port" "Management_wlan2" {
  interface = "wlan2"
  bridge    = "Management"
  disabled  = false
  priority  = 0x80
}

resource "routeros_interface_bridge_port" "Management_ether3" {
  interface = "ether3"
  bridge    = "Management"
  disabled  = false
  priority  = 0x80
  comment   = "Frodo"
}

resource "routeros_interface_bridge_port" "Management_ether4" {
  interface = "ether4"
  bridge    = "Management"
  disabled  = false
  priority  = 0x80
  comment   = "Gandalf"
}

resource "routeros_interface_bridge_port" "Management_ether5" {
  interface = "ether5"
  bridge    = "Management"
  disabled  = false
  priority  = 0x80
  comment   = "Bilbo"
}

