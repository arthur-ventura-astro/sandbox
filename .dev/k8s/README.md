# Local Cluster

## Setup

### Kubernetes Setup
Linux:
```bash
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
```

Mac:
```bash
brew install kubectl
```

Related Docs:
- Kubectl Docs: [Install Tools](https://kubernetes.io/docs/tasks/tools/)

### Minikube Setup
Linux:
```bash
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube && rm minikube-linux-amd64
```

Mac:
```bash
brew install minikube
```

Related Docs:
- Minikube Docs: [Get Started!](https://minikube.sigs.k8s.io/docs/start/?arch=%2Flinux%2Fx86-64%2Fstable%2Fbinary+download)

### Terraform Setup

Linux:
```bash
# Installation
git clone --depth=1 https://github.com/tfutils/tfenv.git ~/.tfenv
echo 'export PATH="$HOME/.tfenv/bin:$PATH"' >> ~/.bash_profile

# Permissions Setup
mkdir -p ~/.local/bin/
. ~/.profile
ln -s ~/.tfenv/bin/* ~/.local/bin
which tfenv
```

Mac:
```bash
brew install tfenv
```

Installing Terraform:
```bash
tfenv install 1.4.0
tfenv use 1.4.0
```

Related Docs:
- Tfenv Docs: [Repository](https://github.com/tfutils/tfenv)
- Terraform Docs: [Overview](https://developer.hashicorp.com/terraform/docs)

## Managing Cluster

Manage Cluster:
```bash
# Set configuration file
export KUBECONFIG=~/.kube/sandbox_config
# Start Cluster
minikube start --embed-certs
# Save the configuration file to use it on airflow
cat $KUBECONFIG > ../../include/.kube
# Stop Cluster
minikube stop
```

Apply configurations:
```bash
# Just for the first time
terraform init
# Apply configurations
terraform apply
# Clean configurations
terraform destroy
```

Prune Cluster:
```bash
minikube stop
minikube delete
```
