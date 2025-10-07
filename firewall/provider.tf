terraform {
  required_providers {
    routeros = {
      source = "terraform-routeros/routeros"
      version = "1.88.0"
    }
  }
}
provider "routeros" {
  hosturl        = "https://192.168.62.1"        # env ROS_HOSTURL or MIKROTIK_HOST
  username       = "terraform"                       # env ROS_USERNAME or MIKROTIK_USER
  password       = "terraform"                            # env ROS_PASSWORD or MIKROTIK_PASSWORD
  insecure       = true                          # env ROS_INSECURE or MIKROTIK_INSECURE
}
