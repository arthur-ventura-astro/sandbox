module "postgres" {
  source = "terraform-aws-modules/rds/aws"

  identifier = "${module.data.project_name}-postgres"

  # All available versions: https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_PostgreSQL.html#PostgreSQL.Concepts
  engine                   = "postgres"
  engine_version           = "14"
  engine_lifecycle_support = "open-source-rds-extended-support-disabled"
  family                   = "postgres14" # DB parameter group
  major_engine_version     = "14"         # DB option group
  instance_class           = "db.t3.small"

  allocated_storage     = 20
  max_allocated_storage = 100

  db_name  = "sandbox"
  username = "postgres"
  port     = module.data.rds_port
  publicly_accessible = true

  manage_master_user_password_rotation              = true
  master_user_password_rotate_immediately           = false
  master_user_password_rotation_schedule_expression = "rate(15 days)"

  multi_az               = false
  create_db_subnet_group = true
  subnet_ids = local.public_subnets

  vpc_security_group_ids = [local.vpc_security_group]

  maintenance_window              = "Mon:00:00-Mon:03:00"
  backup_window                   = "03:00-06:00"
  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]
  create_cloudwatch_log_group     = true

  backup_retention_period = 1
  skip_final_snapshot     = true
}
