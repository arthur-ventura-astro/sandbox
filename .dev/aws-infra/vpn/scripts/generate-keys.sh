# Execute this from "vpn" directory
set -e 
SECRETS_FOLDER=.secrets

openssl genrsa -out $SECRETS_FOLDER/ca.pem 2048
openssl genrsa -out $SECRETS_FOLDER/client.pem 2048