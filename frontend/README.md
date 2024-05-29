# Deploying NextJS on Cluster

## 1. Containerization using Docker

- `sudo docker build -t usmanf07/nextjs-cont:latest .`
- `sudo docker push usmanf07/nextjs-cont:latest`

## 2. Installing the Helm Chart

- `helm install nextjs-chart ./nextjs-chart`
- Check status using `kubectl get pods` or `kubectl get deployments`

## 3. Port-Forwarding
- Once the pod is in running state, use:
`kubectl port-forward service/nextjs-chart 3000:80`

Then the application can be accessed at `http://localhost:3000/`
