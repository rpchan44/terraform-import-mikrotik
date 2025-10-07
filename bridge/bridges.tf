resource "routeros_interface_bridge" "Management" {
  name = "Management"
  mtu  = auto
  protocol_mode = "rstp"
  disabled = false
}

