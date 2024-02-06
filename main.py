from kubernetes import client, config

def get_helm_managed_deployments():
    try:
        # Load the Kubernetes configuration from the default location or kubeconfig file
        config.load_kube_config()

        # Create an instance of the Kubernetes API client for deployments
        api_instance = client.AppsV1Api()

        # Get deployments with the specified label selector
        deployments = api_instance.list_deployment_for_all_namespaces(label_selector='app.kubernetes.io/managed-by=Helm')

        # Use a set to keep track of unique namespace names
        unique_namespaces = set()

        # Collect unique namespace names
        for deployment in deployments.items:
            unique_namespaces.add(deployment.metadata.namespace)

        # Display unique namespace names
        for namespace in unique_namespaces:
            print(f"Namespace: {namespace}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    get_helm_managed_deployments()
