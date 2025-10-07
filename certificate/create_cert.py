#!/usr/bin/env python3
import librouteros

# -----------------------------
# Router and Certificate Details
# -----------------------------
ROUTER_HOST = '192.168.62.1'
ROUTER_USER = 'terraform'
ROUTER_PASSWORD = 'terraform'

CA_NAME = "sysad-ca-cert"
CA_CN = "ca"
WEBFIG_NAME = "webfig"
WEBFIG_CN = "192.168.62.1"

# Certificate validity in days
CA_DAYS = 3650          # 10 years
WEBFIG_DAYS = 3650      # ~2 years

COUNTRY = "PH"
LOCALITY = "Manila"
ORGANIZATION = "Digital"

DISABLED_SERVICES = { "ftp": 21, "telnet": 23, "www": 80, "ssh": 22 }
ENABLED_SERVICES = { "winbox": 8291 }
SSL_SERVICES = { "api": 8728, "api-ssl": 8729, "www-ssl": 443 }

# -----------------------------
# Connect to MikroTik API
# -----------------------------
def connect_api():
    api = librouteros.connect(
        host=ROUTER_HOST,
        username=ROUTER_USER,
        password=ROUTER_PASSWORD,
        use_ssl=False
    )
    return api

# -----------------------------
# Certificate Utility Functions
# -----------------------------
def get_cert_id(api, name):
    certs = list(api('/certificate/print'))
    cert = next((c for c in certs if c['name'] == name), None)
    if not cert:
        raise ValueError(f"Certificate '{name}' not found")
    return cert['.id']

def create_ca(api):
    cmd = {
        "name": CA_NAME,
        "common-name": CA_CN,
        "key-usage": "key-cert-sign",
        "subject-alt-name": "",
        "country": COUNTRY,
        "locality": LOCALITY,
        "organization": ORGANIZATION,
        "days-valid": CA_DAYS
    }
    list(api('/certificate/add', **cmd))
    ca_id = get_cert_id(api, CA_NAME)
    list(api('/certificate/set', **{'.id': ca_id, 'trusted': 'yes'}))
    print(f"✅ CA '{CA_NAME}' created and trusted with ID {ca_id}")
    return ca_id

def self_sign_ca(api, ca_name):
    ca_id = get_cert_id(api, ca_name)
    list(api('/certificate/sign', **{'.id': ca_id}))
    print(f"✅ CA '{ca_name}' self-signed")

def create_request(api, name, cn, days=365):
    cmd = {
        "name": name,
        "common-name": cn,
        "key-usage": "tls-server",
        "subject-alt-name": "",
        "country": COUNTRY,
        "locality": LOCALITY,
        "organization": ORGANIZATION,
        "days-valid": days
    }
    list(api('/certificate/add', **cmd))
    req_id = get_cert_id(api, name)
    print(f"✅ Certificate request '{name}' created with ID {req_id}")
    return req_id

def sign_certificate(api, cert_name, ca_name):
    cert_id = get_cert_id(api, cert_name)
    list(api('/certificate/sign', **{'.id': cert_id, 'ca': ca_name}))
    print(f"✅ Certificate '{cert_name}' signed by CA '{ca_name}'")
    return cert_id

def bind_www_ssl(api, cert_name):
    list(api('/ip/service/set', numbers='www-ssl', certificate=cert_name))
    print(f"✅ Certificate '{cert_name}' bound to www-ssl")

# -----------------------------
# Terraform File Generation (Static)
# -----------------------------
def generate_terraform_files(api):
    tf_lines = []

    # Certificates
    tf_lines.append(f'resource "routeros_system_certificate" "ca-cert" {{\n  name = "{CA_NAME}"\n}}')
    tf_lines.append(f'resource "routeros_system_certificate" "webfig" {{\n  name = "{WEBFIG_NAME}"\n}}')

    # IP Services - Disabled
    for name, port in DISABLED_SERVICES.items():
        tf_lines.append(f'resource "routeros_ip_service" "disabled_{name}" {{\n'
                        f'  numbers  = "{name}"\n'
                        f'  port     = {port}\n'
                        f'  disabled = true\n'
                        f'}}')

    # IP Services - Enabled
    for name, port in ENABLED_SERVICES.items():
        tf_lines.append(f'resource "routeros_ip_service" "enabled_{name}" {{\n'
                        f'  numbers  = "{name}"\n'
                        f'  port     = {port}\n'
                        f'  disabled = false\n'
                        f'}}')

    # IP Services - SSL
    for name, port in SSL_SERVICES.items():
        tf_lines.append(f'resource "routeros_ip_service" "ssl_{name}" {{\n'
                        f'  numbers     = "{name}"\n'
                        f'  port        = {port}\n'
                        f'  tls_version = "only-1.2"\n'
                        f'  certificate = routeros_system_certificate.webfig.name\n'
                        f'}}')

    with open("routeros_certificate.tf", "w") as f:
        f.write("\n\n".join(tf_lines) + "\n")
    print("✅ routeros_certificate.tf written (static resources)")

    # -----------------------------
    # Import File Generation (Static, Duplicate-Free)
    # -----------------------------
    import_lines = [
        f'import {{\n  to = routeros_system_certificate.ca-cert\n  id = "{get_cert_id(api, CA_NAME)}"\n}}',
        f'import {{\n  to = routeros_system_certificate.webfig\n  id = "{get_cert_id(api, WEBFIG_NAME)}"\n}}'
    ]

    # Map static resource names
    static_map = {}
    for name in DISABLED_SERVICES:
        static_map[f'disabled_{name}'] = name
    for name in ENABLED_SERVICES:
        static_map[f'enabled_{name}'] = name
    for name in SSL_SERVICES:
        static_map[f'ssl_{name}'] = name

    services = list(api('/ip/service/print'))
    added = set()
    for svc in services:
        flags = svc.get('flags', '')
        # skip dynamic or connection services
        if 'D' in flags or 'c' in flags:
            continue
        # skip disabled if resource is enabled
        if 'X' in flags and svc['name'] in ENABLED_SERVICES:
            continue

        for tf_resource, svc_name in static_map.items():
            if svc['name'] == svc_name and tf_resource not in added:
                import_lines.append(f'import {{\n  to = routeros_ip_service.{tf_resource}\n  id = "{svc[".id"]}"\n}}')
                added.add(tf_resource)
                break

    with open("import_cert.tf", "w") as f:
        f.write("\n".join(import_lines) + "\n")
    print("✅ import_cert.tf written (static, duplicate-free)")

# -----------------------------
# Main Script
# -----------------------------
def main():
    api = connect_api()
    create_ca(api)
    self_sign_ca(api, CA_NAME)
    create_request(api, WEBFIG_NAME, WEBFIG_CN, days=WEBFIG_DAYS)
    sign_certificate(api, WEBFIG_NAME, CA_NAME)
    bind_www_ssl(api, WEBFIG_NAME)
    generate_terraform_files(api)

if __name__ == "__main__":
    main()

