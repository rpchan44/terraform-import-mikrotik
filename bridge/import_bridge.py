#!/usr/bin/env python3
from librouteros import connect
import socket

# ====== MikroTik API Config ======
HOST = "192.168.62.1"
USER = "terraform"
PASS = "terraform"

# ====== Connect with fallback ======
try:
    api = connect(username=USER, password=PASS, host=HOST, port=8728, timeout=10)
    print("✅ Connected via API (8728)")
except (socket.timeout, OSError):
    print("⚠️ Port 8728 failed, trying API-SSL (8729)...")
    api = connect(username=USER, password=PASS, host=HOST, port=8729, plaintext_login=True, timeout=10)
    print("✅ Connected via API-SSL (8729)")

def safe_name(name: str) -> str:
    """Make Terraform-safe resource names."""
    return name.replace("-", "_").replace(" ", "_").replace(".", "_")

# ====== Fetch Bridges ======
bridges = list(api(cmd="/interface/bridge/print"))
print(f"🔍 Found {len(bridges)} bridges")

# ====== Fetch Bridge Ports ======
ports = list(api(cmd="/interface/bridge/port/print"))
print(f"🔍 Found {len(ports)} bridge ports")

# ====== Create Output Files ======
tf_bridges = open("bridges.tf", "w")
tf_ports = open("bridge_ports.tf", "w")
imp_all = open("import_all.sh", "w")

# ====== Process Bridges ======
for b in bridges:
    name = b.get("name")
    if not name:
        continue
    rid = b.get(".id")
    mtu = b.get("mtu")
    protocol_mode = b.get("protocol-mode")
    disabled = str(b.get("disabled", "false")).lower()
    comment = b.get("comment", "")
    resource_name = safe_name(name)

    tf_bridges.write(f'resource "routeros_interface_bridge" "{resource_name}" {{\n')
    tf_bridges.write(f'  name = "{name}"\n')
    if mtu:
        tf_bridges.write(f'  mtu  = {mtu}\n')
    if protocol_mode:
        tf_bridges.write(f'  protocol_mode = "{protocol_mode}"\n')
    tf_bridges.write(f'  disabled = {disabled}\n')
    if comment:
        tf_bridges.write(f'  comment = "{comment}"\n')
    tf_bridges.write("}\n\n")

    imp_all.write(f'terraform import routeros_interface_bridge.{resource_name} "*{rid}"\n')

# ====== Process Bridge Ports ======
for p in ports:
    iface = p.get("interface")
    bridge = p.get("bridge")
    if not iface or not bridge:
        continue
    rid = p.get(".id")
    path_cost = p.get("path-cost")
    priority = p.get("priority")
    disabled = str(p.get("disabled", "false")).lower()
    comment = p.get("comment", "")
    resource_name = safe_name(f"{bridge}_{iface}")

    tf_ports.write(f'resource "routeros_interface_bridge_port" "{resource_name}" {{\n')
    tf_ports.write(f'  interface = "{iface}"\n')
    tf_ports.write(f'  bridge    = "{bridge}"\n')
    tf_ports.write(f'  disabled  = {disabled}\n')
    if path_cost:
        tf_ports.write(f'  path_cost = {path_cost}\n')
    if priority:
        tf_ports.write(f'  priority  = {priority}\n')
    if comment:
        tf_ports.write(f'  comment   = "{comment}"\n')
    tf_ports.write("}\n\n")

    imp_all.write(f'terraform import routeros_interface_bridge_port.{resource_name} "*{rid}"\n')

# ====== Close Files ======
tf_bridges.close()
tf_ports.close()
imp_all.close()

print("\n✅ Generated files:")
print("  - bridges.tf")
print("  - bridge_ports.tf")
print("  - import_all.sh")
print("\nRun to import everything:")
print("  chmod +x import_all.sh && ./import_all.sh")

