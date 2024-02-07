# Deploying Flask Server on Cluster

## 1. Containerization using Docker

- `sudo docker build -t usmanf07/backend:latest .`
- `sudo docker push usmanf07/backend:latest`

## 2. Installing the Helm Chart

- `helm install flask-chart ./flask-chart`
- Check status using `kubectl get pods` or `kubectl get deployments`

## 3. Port-Forwarding
- Once the pod is in running state, use: `kubectl port-forward service/flask-chart 5000:5000`
