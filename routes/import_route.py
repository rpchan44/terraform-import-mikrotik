#!/usr/bin/env python3
"""
import_routes_with_imports.py
- Uses librouteros to read routing tables, routing rules, and static ip routes.
- Writes routing_import.tf and routing_imports.sh (chmod +x).
- Optionally executes terraform import commands if terraform is available in PATH.
"""
from librouteros import connect
import re
import socket
import os
import subprocess
import shutil

# ---- Connection settings ----
HOST = "192.168.62.1"
USER = "terraform"
PASS = "terraform"
PORT = 8728

TF_OUT = "routing_import.tf"
IMPORT_OUT = "routing_imports.sh"


def connect_mikrotik(host, user, password, port):
    """Connect with fallback to API-SSL (8729)."""
    try:
        api = connect(username=user, password=password, host=host, port=port, timeout=10)
        print(f"✅ Connected to {host}:{port}")
        return api
    except (socket.timeout, OSError) as e:
        print(f"⚠️ API plain failed ({e}), trying API-SSL on 8729...")
        api = connect(username=user, password=password, host=host, port=8729, plaintext_login=True, timeout=10)
        print("✅ Connected via API-SSL (8729)")
        return api


def sanitize_name(s):
    """Terraform-safe resource names (letters, digits, underscore). Ensure not starting with digit."""
    if s is None:
        s = "unnamed"
    s = re.sub(r"[^A-Za-z0-9_]", "_", str(s))
    if not s:
        s = "unnamed"
    if s[0].isdigit():
        s = "r_" + s
    return s


def fmt_value(v):
    """Format a RouterOS value to HCL (string quoted unless boolean/number)."""
    if v is None:
        return None
    # booleans (RouterOS often returns "true"/"false" as strings)
    if isinstance(v, bool):
        return "true" if v else "false"
    s = str(v)
    if s.lower() in ("true", "false"):
        return s.lower()
    # try integer
    try:
        if "." in s:
            float(s)
            return s
        else:
            int(s)
            return s
    except Exception:
        # quote and escape
        escaped = s.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'


def build_routing_tf_and_imports(api):
    tf_blocks = []
    import_cmds = []
    seen_names = set()

    # ---- routing tables (skip dynamic) ----
    print("📥 Fetching /routing/table ...")
    tables = list(api(cmd="/routing/table/print"))
    print(f"✅ Found {len(tables)} routing table entries (including dynamic)")
    for t in tables:
        # Skip dynamic tables like "main" that are not user-created
        if t.get("dynamic") in ("true", True):
            continue
        raw_name = t.get("name", "unnamed")
        name = sanitize_name(raw_name)
        if name in seen_names:
            suffix = t.get(".id", "").replace("*", "")
            name = f"{name}_{suffix}"
        seen_names.add(name)

        lines = [f'resource "routeros_routing_table" "{name}" {{']
        # name is a string
        lines.append(f'  name = {fmt_value(raw_name)}')
        if "fib" in t:
            lines.append(f'  fib  = {fmt_value(t.get("fib"))}')
        if "comment" in t:
            lines.append(f'  comment = {fmt_value(t.get("comment"))}')
        lines.append("}")
        tf_blocks.append("\n".join(lines))

        if ".id" in t:
            import_cmds.append(f"terraform import routeros_routing_table.{name} '{t['.id']}'")

    # ---- routing rules ----
    print("📥 Fetching /routing/rule ...")
    rules = list(api(cmd="/routing/rule/print"))
    print(f"✅ Found {len(rules)} routing rules")
    for r in rules:
        rid = r.get(".id", "").replace("*", "")
        # prefer comment for stable names, fallback to id
        raw_name = r.get("comment") or f"rule_{rid}"
        name = sanitize_name(raw_name)
        if name in seen_names:
            name = f"{name}_{rid}"
        seen_names.add(name)

        lines = [f'resource "routeros_routing_rule" "{name}" {{']
        # include commonly used attributes if present
        for key in ("action", "src-address", "dst-address", "table", "interface", "disabled", "comment"):
            if key in r:
                lines.append(f'  {key.replace("-", "_")} = {fmt_value(r.get(key))}')
        lines.append("}")
        tf_blocks.append("\n".join(lines))

        if ".id" in r:
            import_cmds.append(f"terraform import routeros_routing_rule.{name} '{r['.id']}'")

    # ---- static IP routes ----
    print("📥 Fetching /ip/route ... (excluding dynamic)")
    routes_raw = list(api(cmd="/ip/route/print"))
    # filter dynamic (RouterOS may return dynamic as "true" string or boolean)
    routes = [rr for rr in routes_raw if not (rr.get("dynamic") in ("true", True))]
    print(f"✅ Found {len(routes)} static routes (filtered from {len(routes_raw)})")
    for r in routes:
        rid = r.get(".id", "").replace("*", "")
        dst = r.get("dst-address") or ""
        gw = r.get("gateway") or ""
        name_base = f"{dst}_{gw}" if dst or gw else f"route_{rid}"
        name = sanitize_name(name_base)
        if name in seen_names:
            name = f"{name}_{rid}"
        seen_names.add(name)

        lines = [f'resource "routeros_ip_route" "{name}" {{']
        if "dst-address" in r:
            lines.append(f'  dst_address = {fmt_value(r.get("dst-address"))}')
        if "gateway" in r:
            lines.append(f'  gateway = {fmt_value(r.get("gateway"))}')
        if "distance" in r:
            lines.append(f'  distance = {fmt_value(r.get("distance"))}')
        if "routing-table" in r:
            lines.append(f'  routing_table = {fmt_value(r.get("routing-table"))}')
        if "disabled" in r:
            lines.append(f'  disabled = {fmt_value(r.get("disabled"))}')
        if "comment" in r:
            lines.append(f'  comment = {fmt_value(r.get("comment"))}')
        lines.append("}")
        tf_blocks.append("\n".join(lines))

        if ".id" in r:
            import_cmds.append(f"terraform import routeros_ip_route.{name} '{r['.id']}'")

    return tf_blocks, import_cmds


def write_outputs(tf_blocks, import_cmds):
    # write tf
    with open(TF_OUT, "w") as f:
        f.write("# Generated by import_routes_with_imports.py\n\n")
        f.write("\n\n".join(tf_blocks))
        f.write("\n")
    print(f"✅ Terraform resources written to {TF_OUT}")

    # write import script
    with open(IMPORT_OUT, "w") as f:
        f.write("#!/bin/bash\nset -e\n\n")
        for cmd in import_cmds:
            f.write(cmd + "\n")
    os.chmod(IMPORT_OUT, 0o755)
    print(f"✅ Terraform import script written to {IMPORT_OUT}")


def maybe_execute_imports(import_cmds):
    """Run terraform import commands if terraform exists in PATH."""
    if not import_cmds:
        print("ℹ️ No import commands to run.")
        return
    terraform_path = shutil.which("terraform")
    if not terraform_path:
        print("⚠️ terraform not found in PATH — not executing imports. To run manually:")
        print(f"    ./{IMPORT_OUT}")
        return

    print(f"🚀 Executing {len(import_cmds)} terraform import commands (terraform at {terraform_path})")
    for cmd in import_cmds:
        print("🔗", cmd)
        # run via shell so we keep quoting as written
        subprocess.run(cmd, shell=True)


def main():
    api = connect_mikrotik(HOST, USER, PASS, PORT)
    tf_blocks, import_cmds = build_routing_tf_and_imports(api)
    write_outputs(tf_blocks, import_cmds)
    maybe_execute_imports(import_cmds)
    print("🎉 Done.")


if __name__ == "__main__":
    main()

