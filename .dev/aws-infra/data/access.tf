locals {
  rds_port = 5432
  comm_port = 443
  ssh_port = 22
  dns_port = 53

  tcp_list = [
    local.rds_port,
    local.comm_port,
    local.ssh_port
  ]
  udp_list = [
    local.dns_port
  ]
}

output "tcp_access" {
  value = [ for port in local.tcp_list: tostring(port) ]
}
output "udp_access" {
  value = [ for port in local.udp_list: tostring(port) ]
}

output "rds_port" {
  value = local.rds_port
}

output "comm_port" {
  value = local.comm_port
}

output "ssh_port" {
  value = local.ssh_port
}