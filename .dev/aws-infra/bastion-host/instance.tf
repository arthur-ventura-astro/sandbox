module "ec2_bastion" {
  source                      = "terraform-aws-modules/ec2-instance/aws"
  version                     = "~> 5.3"
  name                        = "${module.data.project_name}-bastion-host"
  instance_type               = "t3.micro"

  ami_ssm_parameter           = local.ami_ssm
  vpc_security_group_ids      = [local.security_group]
  subnet_id                   = local.subnet_id
  key_name                    = local.key_name
  associate_public_ip_address = local.public_ip

  root_block_device           =  [
    {
      volume_type = "gp3"
      encrypted   = true
      volume_size = 10
    }
  ]
  iam_role_policies           =  {
    AmazonSSMFullAccess = "arn:aws:iam::aws:policy/AmazonSSMFullAccess"
  }

  create_iam_instance_profile = true
  enable_volume_tags          = false
  user_data_replace_on_change = true

  user_data                   = templatefile("${path.module}/user_data/amazon-linux.sh", {
    ssm_enabled = true
    ssh_user    = "ec2-user"
  })

  depends_on = [ aws_ssm_parameter.ami ]
}


resource "local_file" "instance_ip" {
  count = local.ssh_resources

  content  = module.ec2_bastion.public_ip
  filename = ".secrets/bastion-host-ip.txt"

  depends_on = [ module.ec2_bastion ]
}

resource "local_file" "instance_id" {
  count = local.ssm_resources

  content  = module.ec2_bastion.id
  filename = ".secrets/bastion-host-id.txt"

  depends_on = [ module.ec2_bastion ]
}