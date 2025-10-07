# Generated automatically by import_firewall.py

resource "routeros_ip_firewall_filter" "back_to_home_vpn" {
  chain = "forward"
  action = "drop"
  comment = "back-to-home-vpn"
}

resource "routeros_ip_firewall_filter" "back_to_home_vpn" {
  chain = "input"
  action = "accept"
  protocol = "udp"
  dst_port = "43245"
  comment = "back-to-home-vpn"
}

resource "routeros_ip_firewall_filter" "special_dummy_rule_to_show_fasttrack_counters" {
  chain = "forward"
  action = "passthrough"
  comment = "special dummy rule to show fasttrack counters"
}

resource "routeros_ip_firewall_filter" "accept_established__related__untracked" {
  chain = "input"
  action = "accept"
  log = "False"
  log_prefix = ""
  comment = "accept established, related, untracked"
}

resource "routeros_ip_firewall_filter" "drop_invalid" {
  chain = "input"
  action = "drop"
  log = "False"
  log_prefix = ""
  comment = "drop invalid"
}

resource "routeros_ip_firewall_filter" "accept_icmp" {
  chain = "input"
  action = "accept"
  protocol = "icmp"
  log = "False"
  log_prefix = ""
  comment = "accept ICMP"
}

resource "routeros_ip_firewall_filter" "accept_to_local_loopback_for_capsman" {
  chain = "input"
  action = "accept"
  dst_address = "127.0.0.1"
  log = "False"
  log_prefix = ""
  comment = "accept to local loopback for capsman"
}

resource "routeros_ip_firewall_filter" "drop_all_not_coming_from_lan" {
  chain = "input"
  action = "drop"
  log = "False"
  log_prefix = ""
  comment = "drop all not coming from LAN"
}

resource "routeros_ip_firewall_filter" "accept_in_ipsec_policy" {
  chain = "forward"
  action = "accept"
  log = "False"
  log_prefix = ""
  comment = "accept in ipsec policy"
}

resource "routeros_ip_firewall_filter" "accept_out_ipsec_policy" {
  chain = "forward"
  action = "accept"
  log = "False"
  log_prefix = ""
  comment = "accept out ipsec policy"
}

resource "routeros_ip_firewall_filter" "fasttrack" {
  chain = "forward"
  action = "fasttrack-connection"
  log = "False"
  log_prefix = ""
  comment = "fasttrack"
}

resource "routeros_ip_firewall_filter" "accept_established__related__untracked" {
  chain = "forward"
  action = "accept"
  log = "False"
  log_prefix = ""
  comment = "accept established, related, untracked"
}

resource "routeros_ip_firewall_filter" "drop_invalid" {
  chain = "forward"
  action = "drop"
  log = "False"
  log_prefix = ""
  comment = "drop invalid"
}

resource "routeros_ip_firewall_filter" "drop_all_from_wan_not_dstnated" {
  chain = "forward"
  action = "drop"
  log = "False"
  log_prefix = ""
  comment = "drop all from WAN not DSTNATed"
}

resource "routeros_ip_firewall_nat" "back_to_home_vpn" {
  chain = "srcnat"
  action = "masquerade"
  in_interface = "back-to-home-vpn"
  comment = "back-to-home-vpn"
}

resource "routeros_ip_firewall_nat" "routeros_ip_firewall_nat__5" {
  chain = "dstnat"
  action = "dst-nat"
  protocol = "tcp"
  dst_address = "10.0.0.7"
  in_interface = "VPN->JJ"
  dst_port = "80,443"
  to_addresses = "192.168.51.9"
  log = "False"
  log_prefix = ""
}

resource "routeros_ip_firewall_nat" "routeros_ip_firewall_nat__d" {
  chain = "dstnat"
  action = "dst-nat"
  protocol = "tcp"
  dst_address = "10.99.99.2"
  in_interface = "VPN->LC"
  dst_port = "80"
  to_addresses = "192.168.51.9"
  to_ports = "3080"
  log = "False"
  log_prefix = ""
}

resource "routeros_ip_firewall_nat" "routeros_ip_firewall_nat__b" {
  chain = "dstnat"
  action = "dst-nat"
  protocol = "udp"
  dst_address = "10.0.0.7"
  in_interface = "VPN->JJ"
  dst_port = "500,4500"
  to_addresses = "192.168.62.232"
  log = "False"
  log_prefix = ""
}

resource "routeros_ip_firewall_nat" "routeros_ip_firewall_nat__1" {
  chain = "srcnat"
  action = "masquerade"
  to_addresses = "192.168.1.4"
  log = "False"
  log_prefix = ""
}
