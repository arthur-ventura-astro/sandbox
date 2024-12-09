# Execute this from "bastion-host" directory
set -e 

PUBLIC_IP=$(cat .secrets/bastion-host.txt)
exec ssh -i ".secrets/bastion-host-key.pem" ec2-user@$PUBLIC_IP