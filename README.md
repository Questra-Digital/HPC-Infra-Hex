# Kubeflow - Configuration

# Installation
- Run the following command in the terminal:
`while ! kustomize build example | kubectl apply -f -; do echo "Retrying to apply resources"; sleep 10; done`
- use `kubectl get pods -n kubeflow` to check the deployment status
- When all pods are running, use `kubectl port-forward svc/istio-ingressgateway -n istio-system --address=0.0.0.0 8080:80` and go to localhost:8080 to view the dashboard.

# Issues

- Currently there are issues in:
1. katib-db-manager ([Issue #7][kf1])
2. metadata-grpc-deployment
3. metadata-writer
4. ml-pipeline

Fixing katib-db-manager will probably fix other crashes too.

[kf1]: https://github.com/Questra-Digital/HPC-Infra-Hex/issues/7