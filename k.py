from flask import Flask, jsonify, request
from pymongo import MongoClient
import yaml
from kubernetes import client, config
from kubernetes.client.rest import ApiException
import uuid
import subprocess
import threading
import asyncio
from pyhelm3 import Client
from kubernetes.stream import stream

app = Flask(__name__)



# MongoDB connection
cliente = MongoClient('mongodb+srv://orthoimplantsgu:pakistan@cluster0.eegqz25.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
db = cliente['kubernetes_db']

# Kubernetes API client
config.load_kube_config()
k8s_client = client.ApiClient()
Coreapi = client.CoreV1Api()
current_node = None

# Function to update current_node based on pods in default namespace
def update_current_node():
    global current_node
    try:
        # Get pods in default namespace
        pods = Coreapi.list_namespaced_pod(namespace="default").items
        
        # Find the pod with name starting with "pythonserver"
        for pod in pods:
            if pod.metadata.name.startswith("pythonserver"):
                current_node = pod.metadata.name
                break
    except Exception as e:
        print(f"Error updating current node: {e}")


@app.route('/')
def hello():
    update_current_node()
    return jsonify({"current_node": current_node})
class ToolModal:
    def __init__(self, tool_name, helm_command, installed):
        self.tool_name = tool_name
        self.helm_command = helm_command
        self.installed = installed

@app.route('/insert-tool', methods=['POST'])
def insert_tool_data():
    try:
        # Accessing a collection in MongoDB
        # Replace 'tools' with your desired collection name
        collection = db['tools']

        # Extract data from the POST request
        data = request.json

        # Create a new ToolModal object
        tool = ToolModal(data['tool_name'], data['helm_command'], data['installed'])

        # Insert the data into the collection
        collection.insert_one(tool.__dict__)

        return jsonify({"message": "Tool information inserted successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# Define the Modal
class InstallationModal:
    def __init__(self, file_name, file_content, installed):
        self.file_name = file_name
        self.file_content = file_content
        self.installed = installed

# Check MongoDB connection status
def check_mongo_connection():
    try:
        cliente.server_info()
        print("MongoDB connected successfully!")
    except Exception as e:
        print("Error connecting to MongoDB:", e)

check_mongo_connection()

# Endpoint to insert data into the MongoDB collection
@app.route('/insert', methods=['POST'])
def insert_modal_data():
    try:
        # Accessing a collection in MongoDB
        # Replace 'files' with your desired collection name
        collection = db['files']

        # Extract data from the POST request
        data = request.json

        # Create a new InstallationModal object
        modal = InstallationModal(data['file_name'], data['file_content'], data['installed'])

        # Insert the data into the collection
        collection.insert_one(modal.__dict__)

        return jsonify({"message": "Data inserted successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint to retrieve all files from the MongoDB collection
@app.route('/files', methods=['GET'])
def get_files():
    try:
        # Accessing the 'files' collection
        collection = db['files']

        # Fetch all documents from the collection
        files = list(collection.find({}, {"_id": 0}))

        return jsonify(files)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint to get the file content based on file name and create the file
@app.route('/file/<file_name>', methods=['GET'])
def get_file_content(file_name):
    try:
        # Accessing the 'files' collection
        collection = db['files']

        # Find the document with the given file name
        file_data = collection.find_one({"file_name": file_name})

        if file_data:
            # Write the file content to a new file
            with open(file_name, "w") as file:
                file.write(file_data["file_content"])
            
            return jsonify({"message": f"File '{file_name}' created with content"})
        else:
            return jsonify({"error": "File not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint to apply Kubernetes configuration from file using Kubernetes Python client
@app.route('/createstorage/<namespace>/<file_name>', methods=['GET'])
def apply_kubernetes_config(namespace, file_name):
    try:
        # Read the YAML file content
        with open(file_name, 'r') as file:
            body = yaml.safe_load(file)

        # Create the API instance for StorageClass
        storage_api = client.StorageV1Api()

        # Apply the StorageClass configuration
        storage_api.create_storage_class(body)

        return jsonify({"message": f"Applied StorageClass configuration from '{file_name}' in namespace '{namespace}'"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint to create PersistentVolume (PV) using Kubernetes Python client

@app.route('/createpv/<namespace>/<file_name>', methods=['GET'])
def create_persistent_volume(namespace, file_name):
    try:
        # Read the YAML file content
        with open(file_name, 'r') as file:
            body = yaml.safe_load(file)

        # Generate a unique name for the PV
        pv_name = f"{body['metadata']['name']}-{str(uuid.uuid4())[:8]}"

        # Update the PV name in the YAML body
        body['metadata']['name'] = pv_name

        # Create the API instance for PersistentVolume
        pv_api = client.CoreV1Api()

        # Create the PersistentVolume in the specified namespace
        pv_api.create_persistent_volume(body=body)

        return jsonify({"message": f"Created PersistentVolume '{pv_name}' from '{file_name}' in namespace '{namespace}'"})
    except FileNotFoundError:
        return jsonify({"error": "File not found."}), 404
    except yaml.YAMLError as e:
        return jsonify({"error": f"YAML syntax error: {str(e)}"}), 400
    except ApiException as e:
        return jsonify({"error": f"Kubernetes API error: {e.reason}"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500






@app.route('/create-jupyterhub', methods=['GET'])
def create_jupyterhub():
    try:
       
        pv_file_name = "my-nfs-pv.yaml"
        result = get_file_content(pv_file_name)

        if result.status_code != 200:
            return result

        valuefile = "values.yaml"
        result = get_file_content(pv_file_name)

        if result.status_code != 200:

            return result

        # Step 2: Call create_persistent_volume() for the first time with the same file
        namespace = "default"
        result1 = create_persistent_volume(namespace, pv_file_name)

        if result1.status_code != 200:
            # Return error response if PV creation failed
            return result1

        # Step 3: Call create_persistent_volume() for the second time with the same file
        result2 = create_persistent_volume(namespace, pv_file_name)

        if result2.status_code != 200:
            # Return error response if PV creation failed
            return result2

        # Step 4: Retrieve JupyterHub tool information from MongoDB
        tool_name = "JupyterHub"
        collection = db['tools']
        jupyter_tool = collection.find_one({"tool_name": tool_name})
        helm_command = ""
        if jupyter_tool:
            helm_command = jupyter_tool.get("helm_command")

        resultfinal =  execute_command(helm_command)
        return jsonify({"message": f"Started execution of Helm command for {tool_name} in the background."})
    
    except Exception as e:
        return jsonify({"error": f"An error occurred: {e}"}), 500

        

def get_pods_in_namespace(namespace):
    try:
        # Create Kubernetes API client
        k8s_client = client.CoreV1Api()

        # Call the Kubernetes API to get the list of pods in the specified namespace
        pods = k8s_client.list_namespaced_pod(namespace=namespace)

        # Extract relevant information from the pods
        pod_list = []
        for pod in pods.items:
            pod_list.append({
                "name": pod.metadata.name,
                "status": pod.status.phase,
                "namespace": pod.metadata.namespace,
            })

        return pod_list
    except Exception as e:
        return {"error": str(e)}


@app.route('/get-pods/<namespace>', methods=['GET'])
def get_pods(namespace):
    try:
        # Call the function to get the list of pods in the specified namespace
        pod_list = get_pods_in_namespace(namespace)

        if "error" in pod_list:
            return jsonify({"error": pod_list["error"]}), 500

        return jsonify({"pods": pod_list})
    except Exception as e:
        return jsonify({"error": str(e)}), 500




def get_proxy_public_node_port(namespace):
    try:
        
        v1 = client.CoreV1Api()
        service_name = "proxy-public"
        service = v1.read_namespaced_service(service_name, namespace)
        node_port = service.spec.ports[0].node_port
        return {"namespace": namespace, "service_name": service_name, "node_port": node_port}

    except Exception as e:
        return {"error": str(e)}

@app.route('/get-node-port/<namespace>', methods=['GET'])
def get_node_port(namespace):
    try:
        node_port_result = get_proxy_public_node_port(namespace)

        if "error" in node_port_result:
            return jsonify({"error": node_port_result["error"]}), 500

        return jsonify(node_port_result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500






output = ""

def pod_exec(name, namespace, command):
    global output

    # Load kubeconfig file
    config.load_kube_config()

    # Create the API client
    api_instance = client.CoreV1Api()

    exec_command = ["/bin/sh", "-c", command]

    resp = stream(api_instance.connect_get_namespaced_pod_exec,
                  name,
                  namespace,
                  command=exec_command,
                  stderr=True, stdin=False,
                  stdout=True, tty=False,
                  _preload_content=False)

    while resp.is_open():
        resp.update(timeout=1)
        stdout = resp.read_stdout() or ""
        stderr = resp.read_stderr() or ""
        output += f"STDOUT: {stdout}\nSTDERR: {stderr}\n"



@app.route('/execute-command')
def execute_command(command):
    global output

    # Get the current node's name
    

    if current_node:
        # Define the command to run
        

        # Execute the pod_exec function in a background thread
        thread = threading.Thread(target=pod_exec, args=(current_node, "default", command))
        thread.start()

        return jsonify({"message": "Command execution started."})
    else:
        return jsonify({"error": "Current node not found."})

@app.route('/get-status')
def get_status():
    global output
    return jsonify({"status": output})



@app.route('/delete-all-pvs', methods=['DELETE'])
def delete_all_pvs():
    try:
        # Get all PersistentVolumes
        pvs = k8s_client.list_persistent_volume().items

        deleted_pvs = []
        for pv in pvs:
            # Check if PV status is "Available" or "Released"
            if pv.status.phase in ["Available", "Released"]:
                # Delete the PV
                try:
                    k8s_client.delete_persistent_volume(pv.metadata.name, body=client.V1DeleteOptions())
                    deleted_pvs.append(pv.metadata.name)
                except ApiException as e:
                    return jsonify({"error": f"Error deleting PV '{pv.metadata.name}': {e}"}), 500

        return jsonify({"message": f"Deleted PVs: {deleted_pvs}"}), 200

    except ApiException as e:
        return jsonify({"error": f"Kubernetes API error: {e.reason}"}), 500
    except Exception as e:
        return jsonify({"error": f"An error occurred: {e}"}), 500



if __name__ == "__main__":
    app.run()

