locals {
  key_name = "${module.data.project_name}-bastion-host-key-pair"
}

module "key_pair" {
  source             = "terraform-aws-modules/key-pair/aws"
  key_name           = local.key_name
  create_private_key = true
}

resource "local_file" "key_pair" {
  count = local.ssh_resources

  content  = module.key_pair.private_key_pem
  filename = ".secrets/bastion-host-key.pem"
  provisioner "local-exec" {
    command = "chmod 600 .secrets/bastion-host-key.pem"
  }
}

