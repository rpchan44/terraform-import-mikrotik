#!/usr/bin/env python3
from librouteros import connect
import re

HOST = "192.168.62.1"
USER = "terraform"
PASS = "terraform"
PORT = 8728


def sanitize_name(name: str) -> str:
    """Make safe Terraform resource names."""
    return re.sub(r"[^a-zA-Z0-9_]", "_", name)


def import_resources(api):
    tf_blocks = []
    import_cmds = []

    # --- interface list ---
    print("📥 Fetching /interface/list ...")
    lists = list(api(cmd="/interface/list/print"))
    print(f"✅ Found {len(lists)} interface lists")

    for r in lists:
        name = sanitize_name(r.get("name", "unnamed"))
        tf_blocks.append(f'resource "routeros_interface_list" "{name}" {{\n  name = "{r["name"]}"\n}}\n')
        if ".id" in r:
            import_cmds.append(f"terraform import routeros_interface_list.{name} '{r['.id']}'")

    # --- interface list members ---
    print("📥 Fetching /interface/list/member ...")
    members = list(api(cmd="/interface/list/member/print"))
    print(f"✅ Found {len(members)} interface list members")

    for r in members:
        name = sanitize_name(f"{r.get('list','list')}_{r.get('interface','iface')}")
        tf_blocks.append(
            f'resource "routeros_interface_list_member" "{name}" {{\n'
            f'  list      = "{r.get("list", "")}"\n'
            f'  interface = "{r.get("interface", "")}"\n}}\n'
        )
        if ".id" in r:
            import_cmds.append(f"terraform import routeros_interface_list_member.{name} '{r['.id']}'")

    # --- romon ---
    print("📥 Fetching /tool/romon ...")
    romon = list(api(cmd="/tool/romon/print"))
    print(f"✅ Found {len(romon)} ROMON entries")

    for r in romon:
        name = sanitize_name(r.get("id", "romon"))
        tf_blocks.append(
            f'resource "routeros_tool_romon" "{name}" {{\n'
            f'  enabled = {str(r.get("enabled", "no")).lower() == "yes"}\n'
            f'}}\n'
        )
        if ".id" in r:
            import_cmds.append(f"terraform import routeros_tool_romon.{name} '{r['.id']}'")

    return tf_blocks, import_cmds


def main():
    print(f"✅ Connecting to {HOST}:{PORT}")
    api = connect(username=USER, password=PASS, host=HOST, port=PORT)
    tf_blocks, import_cmds = import_resources(api)

    with open("interface_list_import.tf", "w") as f:
        f.write("\n".join(tf_blocks))
    with open("interface_list_import.sh", "w") as f:
        f.write("\n".join(import_cmds))

    print("✅ Terraform definitions written to interface_list_import.tf")
    print("✅ Import commands written to interface_list_import.sh")


if __name__ == "__main__":
    main()

