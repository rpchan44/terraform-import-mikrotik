#!/usr/bin/env python3
import os
import re
import sys
import subprocess
import socket
from librouteros import connect

HOST = "192.168.62.1"
USER = "terraform"
PASS = "terraform"
PORT = 8728

TF_FILE = "vpn.tf"
IMPORT_FILE = "vpn_imports.sh"


def connect_mikrotik():
    """Connect to MikroTik RouterOS."""
    try:
        api = connect(username=USER, password=PASS, host=HOST, port=PORT, timeout=10)
        print(f"✅ Connected to {HOST}:{PORT}")
        return api
    except (socket.timeout, OSError) as e:
        print(f"❌ Connection failed: {e}")
        sys.exit(1)


def sanitize_name(name):
    """Make Terraform-safe resource names."""
    return re.sub(r"[^a-zA-Z0-9_]", "_", name.lower().strip()) or "entry"


def make_tf_block(resource, attrs):
    """Generate Terraform block text."""
    lines = [f'resource "{resource}" "{attrs["name"]}" {{']
    for k, v in attrs["fields"].items():
        if v:
            lines.append(f'  {k} = "{v}"')
    lines.append("}\n")
    return "\n".join(lines)


def fetch(api, path, exclude_dynamic=True):
    """Fetch MikroTik path items."""
    rules = []
    for item in api.path(path):
        if exclude_dynamic and item.get("dynamic") == "true":
            continue
        rules.append(item)
    return rules


def main():
    api = connect_mikrotik()
    tf_blocks = []
    import_cmds = []

    # --- SSTP Server ---
    print("📥 Fetching SSTP server config...")
    try:
        sstp_server = api.path("interface/sstp-server/server").get()
        if sstp_server:
            sstp = sstp_server[0]
            name = "sstp_server"
            fields = {
                "enabled": sstp.get("enabled"),
                "certificate": sstp.get("certificate"),
                "authentication": sstp.get("authentication"),
                "default_profile": sstp.get("default-profile"),
                "port": sstp.get("port"),
                "tls_version": sstp.get("tls-version"),
            }
            tf_blocks.append(make_tf_block("routeros_interface_sstp_server", {"name": name, "fields": fields}))
            import_cmds.append(f"terraform import routeros_interface_sstp_server.{name} '.'")
            print("✅ SSTP server found.")
        else:
            print("⚠️ No SSTP server found.")
    except Exception as e:
        print(f"⚠️ SSTP server fetch error: {e}")

    # --- SSTP Clients ---
    print("📥 Fetching SSTP clients...")
    sstp_clients = fetch(api, "interface/sstp-client")
    for c in sstp_clients:
        name = sanitize_name(c.get("name") or c.get(".id"))
        fields = {
            "connect_to": c.get("connect-to"),
            "user": c.get("user"),
            "password": c.get("password"),
            "certificate": c.get("certificate"),
            "verify_server_certificate": c.get("verify-server-certificate"),
            "add_default_route": c.get("add-default-route"),
            "profile": c.get("profile"),
            "comment": c.get("comment"),
        }
        tf_blocks.append(make_tf_block("routeros_interface_sstp_client", {"name": name, "fields": fields}))
        import_cmds.append(f"terraform import routeros_interface_sstp_client.{name} '{c['.id']}'")
    print(f"✅ Found {len(sstp_clients)} SSTP clients")

    # --- WireGuard Interfaces (server/client unified) ---
    print("📥 Fetching WireGuard interfaces...")
    wg_intfs = fetch(api, "interface/wireguard")
    for wg in wg_intfs:
        name = sanitize_name(wg.get("name") or wg.get(".id", "wg"))
        fields = {
            "listen_port": wg.get("listen-port"),
            "private_key": wg.get("private-key"),
            "mtu": wg.get("mtu"),
            "comment": wg.get("comment"),
        }
        tf_blocks.append(make_tf_block("routeros_interface_wireguard", {"name": name, "fields": fields}))
        import_cmds.append(f"terraform import routeros_interface_wireguard.{name} '{wg['.id']}'")
    print(f"✅ Found {len(wg_intfs)} WireGuard interfaces")

    # --- WireGuard Peers ---
    print("📥 Fetching WireGuard peers...")
    wg_peers = fetch(api, "interface/wireguard/peers")
    for peer in wg_peers:
        name = sanitize_name(peer.get("comment") or peer.get(".id", "peer"))
        fields = {
            "public_key": peer.get("public-key"),
            "allowed_address": peer.get("allowed-address"),
            "endpoint_address": peer.get("endpoint-address"),
            "endpoint_port": peer.get("endpoint-port"),
            "interface": peer.get("interface"),
            "persistent_keepalive": peer.get("persistent-keepalive"),
            "comment": peer.get("comment"),
        }
        tf_blocks.append(make_tf_block("routeros_interface_wireguard_peer", {"name": name, "fields": fields}))
        import_cmds.append(f"terraform import routeros_interface_wireguard_peer.{name} '{peer['.id']}'")
    print(f"✅ Found {len(wg_peers)} WireGuard peers")

    # --- IPsec Configurations ---
    ipsec_sections = {
        "ip/ipsec/profile": "routeros_ip_ipsec_profile",
        "ip/ipsec/proposal": "routeros_ip_ipsec_proposal",
        "ip/ipsec/peer": "routeros_ip_ipsec_peer",
        "ip/ipsec/policy": "routeros_ip_ipsec_policy",
        "ip/ipsec/identity": "routeros_ip_ipsec_identity",
    }

    for path, tf_type in ipsec_sections.items():
        print(f"📥 Fetching {path}...")
        entries = fetch(api, path)
        for item in entries:
            name = sanitize_name(item.get("name") or item.get(".id", "entry"))
            fields = {k.replace("-", "_"): v for k, v in item.items() if not k.startswith(".")}
            tf_blocks.append(make_tf_block(tf_type, {"name": name, "fields": fields}))
            import_cmds.append(f"terraform import {tf_type}.{name} '{item['.id']}'")
        print(f"✅ Found {len(entries)} entries in {path}")

    # --- Write Files ---
    with open(TF_FILE, "w") as f:
        f.write("# Generated by import_vpn_full.py\n\n")
        f.write("\n".join(tf_blocks))
    print(f"✅ Terraform config written to {TF_FILE}")

    with open(IMPORT_FILE, "w") as f:
        f.write("#!/bin/bash\n# Generated by import_vpn_full.py\n\n")
        for cmd in import_cmds:
            f.write(cmd + "\n")
    os.chmod(IMPORT_FILE, 0o755)
    print(f"✅ Import commands written to {IMPORT_FILE}")

    # Execute imports (optional)
    print("🚀 Running terraform import commands...\n")
    for cmd in import_cmds:
        print("🔗", cmd)
        try:
            subprocess.run(cmd.split(), check=False)
        except FileNotFoundError:
            print("⚠️ Terraform not found. Skipping execution.")

    print("\n🎉 All VPN (SSTP, WireGuard, IPsec) server/client resources exported and imported!")


if __name__ == "__main__":
    main()

