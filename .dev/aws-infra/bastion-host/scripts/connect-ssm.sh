# Execute this from "bastion-host" directory
set -e 

INSTANCE_ID=$(cat .secrets/bastion-host-id.txt)
exec aws ssm start-session --target $INSTANCE_ID --profile training --region us-east-2