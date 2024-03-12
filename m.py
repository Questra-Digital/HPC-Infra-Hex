import asyncio
from pyhelm3 import Client
import yaml
import pathlib

# Function to load values from your values.yaml file
def load_values(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

# Async function to install JupyterHub
async def install_jupyterhub():
    # Initialize the client, assuming default kubeconfig and Helm paths
    client = Client()

    # Load your custom values from values.yaml
    values = load_values('values.yaml')

    # Pull the chart for JupyterHub from its repository
    # Adjust the 'chart_ref', 'repo', and 'version' as necessary
    async with client.pull_chart('jupyterhub', repo='https://jupyterhub.github.io/helm-chart/') as chart_path:
        # Ensure or upgrade the JupyterHub release with your custom values
        # Adjust 'release_name', 'namespace', and other parameters as needed
        print(chart_path)
        await client.install_or_upgrade_release(
            'my-jupyterhub-release',
            chart_path,
            values,
            create_namespace=True,
            namespace='jhub',
            wait=True,
            cleanup_on_fail=True
        )
        print("hello")

# Run the install function
asyncio.run(install_jupyterhub())
