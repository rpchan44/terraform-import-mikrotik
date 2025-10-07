#!/usr/bin/env python3
from librouteros import connect
import os

# ======= CONFIGURATION =======
HOST = "192.168.62.1"
USER = "terraform"
PASS = "terraform"
PORT = 8728

# ======= CONNECT TO MIKROTIK =======
api = connect(username=USER, password=PASS, host=HOST, port=PORT)
print(f"✅ Connected to {HOST}")

# ======= FETCH INTERFACES =======
interfaces = list(api(cmd="/interface/print"))
print(f"🔍 Found {len(interfaces)} interfaces")

# ======= PREPARE OUTPUT FILES =======
tf_file = open("interfaces.tf", "w")
import_file = open("import_interfaces.sh", "w")

def safe_name(name):
    """Make Terraform-safe name"""
    return name.replace("-", "_").replace(" ", "_").replace(".", "_")

# ======= PROCESS EACH INTERFACE =======
for iface in interfaces:
    name = iface.get("name")
    if not name:
        continue

    iface_id = iface.get(".id")
    iface_type = iface.get("type", "ethernet")
    disabled = str(iface.get("disabled", "false")).lower()
    mtu = iface.get("mtu")
    mac = iface.get("mac-address", "")
    comment = iface.get("comment", "")
    resource_name = safe_name(name)

    # Map MikroTik type to Terraform resource
    if iface_type == "ether":
        tf_type = "routeros_interface_ethernet"
    elif iface_type == "bridge":
        tf_type = "routeros_interface_bridge"
    elif iface_type == "vlan":
        tf_type = "routeros_interface_vlan"
    elif iface_type == "bonding":
        tf_type = "routeros_interface_bonding"
    else:
        tf_type = "routeros_interface"

    # ======= WRITE .TF RESOURCE =======
    tf_file.write(f'resource "{tf_type}" "{resource_name}" {{\n')
    tf_file.write(f'  name     = "{name}"\n')
    if mtu:
        tf_file.write(f'  mtu      = {mtu}\n')
    if mac:
        tf_file.write(f'  mac_address = "{mac}"\n')
    tf_file.write(f'  disabled = {disabled}\n')
    if comment:
        tf_file.write(f'  comment  = "{comment}"\n')
    tf_file.write("}\n\n")

    # ======= WRITE IMPORT COMMAND =======
    import_file.write(f'terraform import {tf_type}.{resource_name} "*{iface_id}"\n')

tf_file.close()
import_file.close()

print("✅ Generated:")
print("  - interfaces.tf")
print("  - import_interfaces.sh")
print("Run:")
print("  chmod +x import_interfaces.sh && ./import_interfaces.sh")

