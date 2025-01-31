source ../../../.env

export KUBECONFIG=~/.kube/sandbox_config
aws eks --region us-east-2 update-kubeconfig --name astro-sandbox-cluster --role-arn arn:aws:iam::$PROJECT_ID:role/astro-sandbox-deployments

cat $KUBECONFIG | yq -P -p yaml -o json > .secrets/config.json