resource "routeros_system_certificate" "ca-cert" {
  name = "ca-cert"
}

resource "routeros_system_certificate" "webfig" {
  name = "webfig"
}

resource "routeros_ip_service" "disabled_ftp" {
  numbers  = "ftp"
  port     = 21
  disabled = true
}

resource "routeros_ip_service" "disabled_telnet" {
  numbers  = "telnet"
  port     = 23
  disabled = true
}

resource "routeros_ip_service" "disabled_www" {
  numbers  = "www"
  port     = 80
  disabled = true
}

resource "routeros_ip_service" "disabled_ssh" {
  numbers  = "ssh"
  port     = 22
  disabled = true
}

resource "routeros_ip_service" "enabled_winbox" {
  numbers  = "winbox"
  port     = 8291
  disabled = false
}

resource "routeros_ip_service" "ssl_api" {
  numbers     = "api"
  port        = 8728
  tls_version = "only-1.2"
  certificate = routeros_system_certificate.webfig.name
}

resource "routeros_ip_service" "ssl_api-ssl" {
  numbers     = "api-ssl"
  port        = 8729
  tls_version = "only-1.2"
  certificate = routeros_system_certificate.webfig.name
}

resource "routeros_ip_service" "ssl_www-ssl" {
  numbers     = "www-ssl"
  port        = 443
  tls_version = "only-1.2"
  certificate = routeros_system_certificate.webfig.name
}
