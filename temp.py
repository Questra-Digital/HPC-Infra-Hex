from kubernetes import client, config

# Load Kubernetes configuration
config.load_kube_config()

# Create Kubernetes API client
api_instance = client.CoreV1Api()

# Get information about nodes
print("Nodes in the cluster:")
nodes = api_instance.list_node()
for node in nodes.items:
    print(f"Node Name: {node.metadata.name}, Status: {node.status.node_info.kubelet_version}")

# Other operations can be similarly performed using the Kubernetes Python client

