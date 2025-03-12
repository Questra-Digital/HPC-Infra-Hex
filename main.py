from flask import Flask, jsonify, request
from pymongo import MongoClient
import yaml
from kubernetes import client, config
from kubernetes.client.rest import ApiException
import uuid
import time
import subprocess
import threading
import asyncio
from pyhelm3 import Client
from kubernetes.stream import stream
from flask_cors import CORS 
import os

app = Flask(__name__)


CORS(app)
# MongoDB connection
cliente = MongoClient('mongodb://orthoimplantsgu:pakistan@ac-cpo8knv-shard-00-00.eegqz25.mongodb.net:27017,ac-cpo8knv-shard-00-01.eegqz25.mongodb.net:27017,ac-cpo8knv-shard-00-02.eegqz25.mongodb.net:27017/?ssl=true&replicaSet=atlas-4i34th-shard-0&authSource=admin&retryWrites=true&w=majority&appName=Cluster0')
db = cliente['kubernetes_db']

# Kubernetes API client
config.load_kube_config()
k8s_client = client.ApiClient()
Coreapi = client.CoreV1Api()
current_node = None
output = {}

@app.route('/reset-installed', methods=['GET'])
def reset_installed():
    try:
        # Accessing the 'tools' collection
        collection = db['tools']

        # Update all documents in the collection, setting 'installed' to false
        collection.update_many({}, {"$set": {"installed": "false"}})

        return jsonify({"message": "All tools' 'installed' status reset to false successfully."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/tools', methods=['GET'])
def get_tools():
    try:
        # Accessing the 'files' collection
        collection = db['tools']

        # Fetch all documents from the collection with tool ID
        tools = list(collection.find({}))
        for tool in tools:
            tool['_id'] = str(tool['_id'])
        return jsonify(tools)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/get-tool-details/<tool_id>', methods=['GET'])
def get_tool_details(tool_id):
    try:
        # Accessing the 'tools' collection
        collection = db['tools']
        tool = collection.find_one({"_id": ObjectId(tool_id)})

        if tool is None:
            return jsonify({"error": "Tool not found"}), 404

        namespace = tool.get("namespace")
        service = tool.get("service")

        return jsonify({"namespace": namespace, "service": service}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/get-tool-id/<tool_name>', methods=['GET'])
def get_tool_id(tool_name):
    try:
        # Accessing the 'tools' collection
        collection = db['tools']

        # Find the tool with the specified name
        tool = collection.find_one({"tool_name": tool_name})
        print(tool_name)
        if tool is None:
            return jsonify({"error": "Tool not found"}), 404

        # Return the tool ID
        return jsonify({"tool_id": str(tool['_id'])}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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
        print(current_node)
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

# Endpoint to login for the user
@app.route('/login', methods=['POST'])
def login_user():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')


        # Accessing the 'users' collection
        collection = db['roles']

        # Find the user with the given username
        user = collection.find_one({"username": username})

        if user:
            role = user.get('role')
            # Check user's role
            if role in ['admin', 'root', 'simple user']:
                # Authenticate the user based on the role
                if user['password'] == password:
                     user_id = str(user.get('_id'))  # Extract and convert _id to string
                     print(user_id)
                     return jsonify({"user_id": user_id, "username": username, "role": role}), 200
                else:
                    return jsonify({"error": "Invalid password"}), 401
            else:
                return jsonify({"error": "Invalid role"}), 401
        else:
            return jsonify({"error": "User not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Get All the users from database

@app.route('/users', methods=['GET'])
def get_all_users():
    try:
        # Accessing the 'roles' collection
        collection = db['roles']

        # Find all users in the collection
        users = list(collection.find({}, {"_id": 0, "username": 1, "role": 1}))

        # Return the list of users
        return jsonify({"users": users}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Endpoint to add a new user
@app.route('/add-user', methods=['POST'])
def add_user():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')
        role = data.get('role')

        # Accessing the 'roles' collection
        collection = db['roles']

        # Check if the user already exists
        existing_user = collection.find_one({"username": username})
        if existing_user:
            return jsonify({"error": "User already exists"}), 400

        # Insert the new user into the collection
        new_user = {
            "username": username,
            "password": password,
            "email": email,
            "role": role
        }
        collection.insert_one(new_user)
        
        return jsonify({"message": "User added successfully"}), 201
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
        # print(file_data)
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

# Endpoint to gets the namespaces and create the namespace if it does not exist, using Kubernetes Python client
@app.route('/namespace/<namespace>', methods=['GET'])
def create_namespace(namespace):
    try:
        # Create the API instance for Namespace
        api_instance = client.CoreV1Api()

        # Define the Namespace body
        body = client.V1Namespace(metadata=client.V1ObjectMeta(name=namespace))

        # Check if the Namespace already exists
        namespaces = api_instance.list_namespace()
        namespace_list = [ns.metadata.name for ns in namespaces.items]

        if namespace in namespace_list:
            return jsonify({"message": f"Namespace '{namespace}' already exists"}), 200
        else:
            # Create the Namespace
            api_instance.create_namespace(body=body)

            return jsonify({"message": f"Namespace '{namespace}' created successfully"}), 200
    except ApiException as e:
        return jsonify({"error": f"Kubernetes API error: {e.reason}"}), 500
    except Exception as e:
        return jsonify({"error": str (e)}), 500

# Endpoint to delete the namespace using Kubernetes Python client
@app.route('/delete-namespace/<namespace>', methods=['DELETE'])
def delete_namespace(namespace):
    try:
        # Create the API instance for Namespace
        api_instance = client.CoreV1Api()

        # Delete the Namespace
        api_instance.delete_namespace(name=namespace)

        return jsonify({"message": f"Namespace '{namespace}' deleted successfully"}), 200
    except ApiException as e:
        return jsonify({"error": f"Kubernetes API error: {e.reason}"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint to create PersistentVolume (PVC) by applying the my-nfs-pvc.yaml file
@app.route('/createpvc/<namespace>/<file_name>/<pvc_name>', methods=['GET'])
def create_persistent_volume_claim(namespace, file_name, pvc_name):
    try:
        # Checks if the pvc already exists with the name 'data-my-mariadb'
        pvc = Coreapi.list_namespaced_persistent_volume_claim(namespace)
        pvc_list = [p.metadata.name for p in pvc.items]
        if pvc_name in pvc_list:
            return jsonify({"message": "PersistentVolumeClaim '{pvc_name}' already exists"}), 200
        
        # Read the YAML file content
        with open(file_name, 'r') as file:
            pvc_yaml = yaml.safe_load(file)

        # Update the PVC name in the YAML content
        pvc_yaml['metadata']['name'] = pvc_name
        pvc_yaml['metadata']['namespace'] = namespace

        # Write the updated YAML content to a temporary file
        temp_file_name = f"temp_{file_name}"
        with open(temp_file_name, 'w') as temp_file:
            yaml.dump(pvc_yaml, temp_file)

        # Construct the kubectl apply command
        command = f"kubectl apply -f {temp_file_name} --namespace {namespace}"

        # Execute the kubectl command
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            return jsonify({"error": f"Failed to apply PersistentVolumeClaim {file_name} in {namespace} namespace: {result.stderr}"}), 500
        
        return jsonify({"message": f"PersistentVolumeClaim {file_name} applied successfully in {namespace} namespace."}), 200
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

# Endpoint to delete PersistentVolumeClaim (PVC) by name using Kubernetes Python client
@app.route('/deletepvc/<namespace>/<pvc_name>', methods=['DELETE'])
def delete_persistent_volume_claim(pvc_name, namespace):
    try:
        # Create the API instance for PersistentVolumeClaim
        pvc_api = client.CoreV1Api()

        # Get the list of PersistentVolumeClaims in the specified namespace
        pvcs = pvc_api.list_namespaced_persistent_volume_claim(namespace)

        # Delete the PersistentVolumeClaim with the specified name
        for pvc in pvcs.items:
            if pvc.metadata.name == pvc_name:
                helm_command = f"kubectl delete persistentvolumeclaim {pvc.metadata.name} --namespace {namespace}"
                result = subprocess.run(helm_command, shell=True, capture_output=True, text=True)
                if result.returncode != 0:
                    return jsonify({"error": f"Failed to delete PersistentVolumeClaim {pvc.metadata.name}: {result.stderr}"}), 500
                
        return jsonify({"message": f"Deleted PersistentVolumeClaim '{pvc_name}' in namespace '{namespace}'"}), 200
    
    except ApiException as e:
        return jsonify({"error": f"Kubernetes API error: {e.reason}"}), 500
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

# Endpoint to create PersistentVolume (PV) by applying the my-nfs-pv.yaml file
@app.route('/createpv/<namespace>/<file_name>/<pv_name>', methods=['GET'])
def create_pv(namespace, file_name, pv_name):
    try:
        # Checks if the pv already exists with the name 'mariadb-pv'
        pv = Coreapi.list_persistent_volume()
        pv_list = [p.metadata.name for p in pv.items]
        if pv_name in pv_list:
            return jsonify({"message": "PersistentVolume '{pv_name}' already exists"}), 200
        
        # Read the YAML file content
        with open(file_name, 'r') as file:
            pv_yaml = yaml.safe_load(file)

        # Update the PVC name in the YAML content
        pv_yaml['metadata']['name'] = pv_name

        # Write the updated YAML content to a temporary file
        temp_file_name = f"temp_{file_name}"
        with open(temp_file_name, 'w') as temp_file:
            yaml.dump(pv_yaml, temp_file)

        # Construct the kubectl apply command
        command = f"kubectl apply -f {temp_file_name} --namespace {namespace}"

        # Execute the kubectl command
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            return jsonify({"error": f"Failed to apply PersistentVolume {file_name} in {namespace} namespace: {result.stderr}"}), 500
        
        return jsonify({"message": f"PersistentVolume {file_name} applied successfully in {namespace} namespace."}), 200
    
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

# Endpoint to delete all PersistentVolume (PV) by similar starting names using Kubernetes Python client
@app.route('/deletepv/<namespace>/<pv_name>', methods=['DELETE'])
def delete_pv(pv_name, namespace):
    try:
        # Create the API instance for PersistentVolume
        pv_api = client.CoreV1Api()

        # Get the list of PersistentVolumes in the specified namespace
        pvs = pv_api.list_persistent_volume()

        # Delete all PersistentVolumes with names starting with the specified name
        for pv in pvs.items:
            if pv.metadata.name.startswith(pv_name):
                helm_command = f"kubectl delete persistentvolume {pv.metadata.name}"
                result = subprocess.run(helm_command, shell=True, capture_output=True, text=True)
                if result.returncode != 0:
                    return jsonify({"error": f"Failed to delete PersistentVolume {pv.metadata.name}: {result.stderr}"}), 500

        return jsonify({"message": f"Deleted PersistentVolumes starting with '{pv_name}' in namespace '{namespace}'"}), 200
    except ApiException as e:
        return jsonify({"error": f"Kubernetes API error: {e.reason}"}), 500
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

# Endpoint to install MariaDB using Helm
@app.route('/install-the-tool/<tool_name>', methods=['GET'])
def install_the_tool(tool_name):
    try:
        # Fetch the Helm command from database
        collection = db['tools']
        tool = collection.find_one({"tool_name": tool_name})
        helm_command = ""
        if tool:
            helm_command = tool.get("helm_command")
        else:
            return jsonify({"error": "{tool_name} tool not found in database"}), 404
        
        # Execute the Helm command
        result = subprocess.run(helm_command, shell=True, capture_output=True, text=True)
        
        if result.returncode != 0:
            return jsonify({"error": f"Failed to install {tool_name}: {result.stderr}"}), 500
        
        # Update MongoDB to mark the tool as installed
        collection.update_one(
            {"tool_name": tool.get("tool_name")},
            {"$set": {"installed": "true"}}
        )

        return jsonify({"message": "{tool_name} installed successfully."}), 200
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

# Endpoint to uninstall MariaDB using Helm
@app.route('/uninstall-the-tool/<tool_name>', methods=['GET'])
def uninstall_the_tool(tool_name):
    try:
        print("uninstall-the-tool endpoint called")
        # Fetch the Helm command from database
        collection = db['tools']
        tool = collection.find_one({"tool_name": tool_name})
        helm_command = ""
        namespace_name = ""

        if tool:
            namespace_name = tool.get("namespace")
            helm_command = f"helm uninstall {namespace_name} -n {namespace_name}"
        else:
            return jsonify({"error": "{tool_name} tool not found in database"}), 404
        
        # Execute the Helm command
        result = subprocess.run(helm_command, shell=True, capture_output=True, text=True)
        
        if result.returncode != 0:
            return jsonify({"error": f"Failed to uninstall {tool_name}: {result.stderr}"}), 500
        
        # Update MongoDB to mark the tool as uninstalled
        collection.update_one(
            {"tool_name": tool.get("tool_name")},
            {"$set": {"installed": "false"}}
        )

        return jsonify({"message": "{tool_name} uninstalled successfully."}), 200
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@app.route('/expose-service/<service_name>/<namespace>/<new_service_name>', methods=['GET'])
def expose_service(service_name, namespace, new_service_name):
    try:
        # Create the API instance for Service
        service_api = client.CoreV1Api()

        # Define the Service body
        body = client.V1Service(
            api_version="v1",
            kind="Service",
            metadata=client.V1ObjectMeta(name=new_service_name),
            spec=client.V1ServiceSpec(
                type="NodePort",
                selector={"app.kubernetes.io/name": service_name},  # Match the pod labels
                ports=[
                    client.V1ServicePort(port=80, target_port=80, name="http"),  # HTTP port
                    client.V1ServicePort(port=443, target_port=443, name="https")  # HTTPS port
                ]
            )
        )

        # Create the Service in the specified namespace
        service_api.create_namespaced_service(namespace=namespace, body=body)

        return jsonify({"message": f"{service_name} service exposed using NodePort in namespace '{namespace}'"}), 200
    except ApiException as e:
        return jsonify({"error": f"Kubernetes API error: {e.reason}"}), 500
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
# Endpoint to delete the MariaDB Service by name using Kubernetes Python client
@app.route('/delete-service/<service_name>/<namespace>', methods=['DELETE'])
def delete_service(service_name, namespace):
    try:
        # Create the API instance for Service
        service_api = client.CoreV1Api()

        # First Gets the list of services in the specified namespace
        services = service_api.list_namespaced_service(namespace)

        if service_name not in [service.metadata.name for service in services.items]:
            return jsonify({"message": f"Service '{service_name}' not found in namespace '{namespace}'"}), 200

        # Delete the Service with the specified name
        service_api.delete_namespaced_service(name=service_name, namespace=namespace)

        return jsonify({"message": f"Deleted Service '{service_name}' in namespace '{namespace}'"}), 200
    except ApiException as e:
        return jsonify({"error": f"Kubernetes API error: {e.reason}"}), 500
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

# Endpoint to create PersistentVolume (PV) using Kubernetes Python client
def create_persistent_volume(namespace, file_name, custom_pv_name=None):
    try:
        # Read the YAML file content
        with open(file_name, 'r') as file:
            body = yaml.safe_load(file)

        # Generate a unique name for the PV if no custom name is provided
        if custom_pv_name:
            pv_name = f"{custom_pv_name}-{str(uuid.uuid4())[:8]}"
        else:
            pv_name = f"{body['metadata']['name']}-{str(uuid.uuid4())[:8]}"

        # Update the PV name in the YAML body
        body['metadata']['name'] = pv_name

        # Create the API instance for PersistentVolume
        pv_api = client.CoreV1Api()

        # Create the PersistentVolume in the specified namespace
        pv_api.create_persistent_volume(body=body)

        return {"message": f"Created PersistentVolume '{pv_name}' from '{file_name}' in namespace '{namespace}'"}, 200
    except FileNotFoundError:
        return {"error": "File not found."}, 404
    except yaml.YAMLError as e:
        return {"error": f"YAML syntax error: {str(e)}"}, 400
    except ApiException as e:
        return {"error": f"Kubernetes API error: {e.reason}"}, 500
    except Exception as e:
        return {"error": str(e)}, 500


def create_config_yaml(image_prefix, hub_url):
    data = {
        'config': {
            'BinderHub': {
                'use_registry': True,
                'image_prefix': image_prefix
            }
        }
    }
    if hub_url:
        data['config']['BinderHub']['hub_url'] = hub_url
    return yaml.dump(data)
  
def create_secret_yaml(username, password):
    data = {
        'registry': {
            'username': username,
            'password': password
        }
    }
    return yaml.dump(data)


def bind_binderhub():
  try:
      print("BIND CALLED")
      jhub_tool = get_proxy_public_node_port("bhub")
      ip_address = "http://192.168.56.10:"
      port = jhub_tool["node_port"]
      config_yaml_content = create_config_yaml("usmanf07/binderhub-", ip_address + str(port))

      # Write YAML content to secret.yaml
      with open('config.yaml', 'w') as file:
          file.write(config_yaml_content)

      tool_name = "BinderHub"
      collection = db['tools']
      binder_tool = collection.find_one({"tool_name": tool_name})
      helm_command = ""
      if binder_tool:
          helm_command = binder_tool.get("helm_command")
          helm_command = helm_command.replace("install", "upgrade", 1)
          resultfinal =  execute_command(helm_command, tool_name)
          print(resultfinal)
          return f"ok"
      
  except Exception as e:
      return {"error": f"An error occurred: {e}"}, 500

@app.route('/create-grafana', methods=['GET'])
def create_grafana():
    try:
        tool_name = "Grafana"
        collection = db['tools']
        grafana_tool = collection.find_one({"tool_name": tool_name})
        helm_command = ""
        if grafana_tool:
            execute_command("helm install grafana grafana/grafana --namespace=graf",tool_name)
            collection.update_one(
                {"tool_name": tool_name},
                {"$set": {"installed": "true"}}
            )
            
            return jsonify({"message": f"Started execution of Helm command for {tool_name} in the background."})
    
    except Exception as e:
      return jsonify({"error": f"An error occurred: {e}"}), 500
    
@app.route('/create-prometheus', methods=['GET'])
def create_prometheus():
    try:
        pv_file_name = "prom_pv.yaml"
        result = get_file_content(pv_file_name)

        pvv_file_name = "prom_pvv.yaml"
        result = get_file_content(pv_file_name)

        namespace = "default"
        result1 = create_persistent_volume(namespace, pv_file_name)

        # if result1.status_code != 200:
        #     # Return error response if PV creation failed
        #     return result1

        # Step 3: Call create_persistent_volume() for the second time with the same file
        result2 = create_persistent_volume(namespace, pv_file_name)
        
        tool_name = "Prometheus"
        collection = db['tools']
        prom_tool = collection.find_one({"tool_name": tool_name})
        helm_command = ""
        namespace = "prom"
        command = f"kubectl create namespace {namespace}"
        result = execute_command(command,"Prometheus")
        # if result.get('error'):
        #     return {"error": result['error']}
        if prom_tool:
            execute_command("helm install prometheus prometheus-community/prometheus --namespace=prom",tool_name)
            collection.update_one(
                {"tool_name": tool_name},
                {"$set": {"installed": "true"}}
            )
            
            return jsonify({"message": f"Started execution of Helm command for {tool_name} in the background."})
    
    except Exception as e:
      print(e)
      return jsonify({"error": f"An error occurred: {e}"}), 500
    
@app.route('/create-binderhub', methods=['GET'])
def create_binderhub():
    try:
        pv_file_name = "bhub_pv.yaml"
        pv_result = get_file_content(pv_file_name)

        
        namespace = "bhub"
        result1 = create_persistent_volume(namespace, pv_file_name)

        secret_yaml_content = create_secret_yaml("usmanf07", "Virus@123")

        # Write YAML content to secret.yaml
        with open('secret.yaml', 'w') as file:
            file.write(secret_yaml_content)

        config_yaml_content = create_config_yaml("usmanf07/binderhub-", "")

        # Write YAML content to secret.yaml
        with open('config.yaml', 'w') as file:
            file.write(config_yaml_content)
        
        #execute_command("helm repo add jupyterhub https://jupyterhub.github.io/helm-chart") 
        #execute_command("helm repo update")

        tool_name = "BinderHub"
        collection = db['tools']
        binder_tool = collection.find_one({"tool_name": tool_name})
        helm_command = ""
        if binder_tool:
            helm_command = binder_tool.get("helm_command")

            resultfinal =  execute_command(helm_command, tool_name)
            collection.update_one(
                {"tool_name": tool_name},
                {"$set": {"installed": "true"}}
            )
            time.sleep(10)
            bind_binderhub()
            #time.sleep(1)
            return jsonify({"message": f"Started execution of Helm command for {tool_name} in the background."})
    
    except Exception as e:
      return jsonify({"error": f"An error occurred: {e}"}), 500
   
@app.route('/create-jupyterhub', methods=['GET'])
def create_jupyterhub():
    print("Jupyterhub calld")
    try:
       
        pv_file_name = "bhub_pv.yaml"
        result = get_file_content(pv_file_name)

        # if result.status_code != 200:
            # return result

        valuefile = "values.yaml"
        result = get_file_content(valuefile)
        # if result.status_code != 200:

            # return result

        # Step 2: Call create_persistent_volume() for the first time with the same file
        namespace = "default"
        result1 = create_persistent_volume(namespace, pv_file_name)

        # if result1.status_code != 200:
            # Return error response if PV creation failed
            # return result1

        # Step 3: Call create_persistent_volume() for the second time with the same file
        result2 = create_persistent_volume(namespace, pv_file_name)
        print(result2)
        # if result2.status_code != 200:
            # Return error response if PV creation failed
            # return result2

        # Step 4: Retrieve JupyterHub tool information from MongoDB
        tool_name = "JupyterHub"
        collection = db['tools']
        jupyter_tool = collection.find_one({"tool_name": tool_name})
        helm_command = ""
        if jupyter_tool:
            helm_command = jupyter_tool.get("helm_command")
            print(helm_command)
        print(helm_command)

        resultfinal =  execute_command(helm_command,tool_name)
        collection.update_one(
            {"tool_name": tool_name},
            {"$set": {"installed": "true"}}
        )

        return jsonify({"message": f"Started execution of Helm command for {tool_name} in the background."})
    
    except Exception as e:
        return jsonify({"error": f"An error occurred: {e}"}), 500

@app.route('/create-mariadb', methods=['GET'])
def create_mariadb():
    try:
        global output
        tool_name = "MariaDB"
        # Step 1 : Create the namespace 'mariadb' if it doesn't exist
        namespace = "mariadb"
        result = create_namespace(namespace)
        if result[1] != 200:
            # Return error response if namespace creation failed
            return result
        
        collection = db['tools']
        mariadb_tool = collection.find_one({"tool_name": tool_name})
        mariadb_pvc_name = ""
        mariadb_pv_name = ""
        if mariadb_tool:
            mariadb_pvc_name = mariadb_tool.get("pvc_name")
            mariadb_pv_name = mariadb_tool.get("pv_name")
        else:
            return jsonify({"error": "MariaDB tool not found in database"}), 404
        
        print("Proceeding to create PV")
        # Step 2 : Create the PersistentVolume (PV) for MariaDB if it doesn't exist
        pv_file_name = "my-custom-nfs-pv.yaml"
        result = create_pv(namespace, pv_file_name, mariadb_pv_name)
        print("Result of Create PV:",result)
        if result[1] != 200:
            # Return error response if PV creation failed
            return result

        # Step 3 : Create the PersistentVolumeClaim (PVC) for MariaDB if it doesn't exist
        pvc_file_name = "my-custom-nfs-pvc.yaml"
        result = create_persistent_volume_claim(namespace, pvc_file_name, mariadb_pvc_name)
        if result[1] != 200:
            # Return error response if PVC creation failed
            return result
        
        # Step 4 : Install MariaDB using the install_mariadb() function
        result = install_the_tool(tool_name)
        if result[1] != 200:
            # Return error response if MariaDB installation failed
            return result
        
        output.setdefault("MariaDB", "")
        output["MariaDB"] += "MariaDB installation started successfully.\n"

        # Step 5 : Expose the MariaDB Service using NodePort
        result = expose_service("mariadb",namespace,"mariadb-exposed")
        if result[1] != 200:
            # Return error response if MariaDB Service exposure failed
            return result

        return jsonify({"message": "MariaDB installation started successfully."})
    except Exception as e:
        return jsonify({"error": f"An error occurred: {e}"}), 500
        
# Endpoint to delete the MariaDB installation step by step
@app.route('/delete-mariadb', methods=['DELETE'])
def delete_mariadb():
    try:
        print("delete-mariadb endpoint called")
        # Step 1 : Delete the MariaDB Services
        service_name = "mariadb-exposed"
        result = delete_service(service_name, "mariadb")
        if result[1] != 200:
            # Return error response if MariaDB Service deletion failed
            return result
        service_name = "mariadb"
        result = delete_service(service_name, "mariadb")
        if result[1] != 200:
            # Return error response if MariaDB Service deletion failed
            return result
        service_name = "mariadb-headless"
        result = delete_service(service_name, "mariadb")
        if result[1] != 200:
            # Return error response if MariaDB Service deletion failed
            return result

        print("Service Deleted")
        # Step 2 : Delete the MariaDB installation using Helm
        result = uninstall_the_tool("MariaDB")
        if result[1] != 200:
            # Return error response if MariaDB uninstallation failed
            return result
        
        # Step 3 : Delete the PersistentVolumeClaim (PVC) for MariaDB
        pvc_name = "data-my-mariadb"
        result = delete_persistent_volume_claim(pvc_name, "mariadb")
        if result[1] != 200:
            # Return error response if MariaDB PVC deletion failed
            return result
        
        # Step 4 : Delete the PersistentVolume (PV) for MariaDB
        pv_name = "mariadb-pv"
        result = delete_pv(pv_name, "mariadb")
        if result[1] != 200:
            # Return error response if MariaDB PV deletion failed
            return result

        # Step 5 : Delete the MariaDB namespace
        namespace = "mariadb"
        result = delete_namespace(namespace)
        if result[1] != 200:
            # Return error response if MariaDB namespace deletion failed
            return result
        
        return jsonify({"message": "MariaDB deletion started successfully."})
    except Exception as e:
        return jsonify({"error": f"An error occurred: { e }"}), 500

@app.route('/create-wordpress', methods=['GET'])
def create_wordpress():
    try:
        global output
        tool_name = "Wordpress"
        
        # Step 1: Create the namespace 'wordpress' if it doesn't exist
        namespace = "wordpress"
        result = create_namespace(namespace)
        if result[1] != 200:
            # Return error response if namespace creation failed
            return result
        
        collection = db['tools']
        wordpress_tool = collection.find_one({"tool_name": tool_name})
        wordpress_pvc_name = ""
        wordpress_pv_name = ""
        if wordpress_tool:
            wordpress_pvc_name = wordpress_tool.get("pvc_name")
            wordpress_pv_name = wordpress_tool.get("pv_name")
        else:
            return jsonify({"error": "Wordpress tool not found in database"}), 404
        
        print("Proceeding to create PV")
        
        # Step 2: Create the PersistentVolume (PV) for Wordpress
        pv_file_name = "my-custom-nfs-pv.yaml"
        with open(pv_file_name, 'r') as file:
            pv_yaml = yaml.safe_load(file)
        
        # Update PV metadata and spec for WordPress
        pv_yaml['metadata']['name'] = wordpress_pv_name
        pv_yaml['spec']['nfs']['path'] = "/shared/nfs"  # Update the NFS path if needed
        
        # Save the updated PV YAML to a temporary file
        temp_pv_file_name = "temp-wordpress-pv.yaml"
        with open(temp_pv_file_name, 'w') as temp_file:
            yaml.dump(pv_yaml, temp_file)
        
        # Apply the PV
        result = create_pv(namespace, temp_pv_file_name, wordpress_pv_name)
        print("Result of Create PV:", result)
        if result[1] != 200:
            # Return error response if PV creation failed
            return result
        
        if os.path.exists(temp_pv_file_name):
          os.remove(temp_pv_file_name)
        file_to_remove = f"temp_{temp_pv_file_name}"
        if os.path.exists(file_to_remove):
            os.remove(file_to_remove)

        # Step 3: Create the PersistentVolumeClaim (PVC) for Wordpress
        pvc_file_name = "my-custom-nfs-pvc.yaml"
        with open(pvc_file_name, 'r') as file:
            pvc_yaml = yaml.safe_load(file)
        
        # Update PVC metadata and spec for WordPress
        pvc_yaml['metadata']['name'] = wordpress_pvc_name
        pvc_yaml['metadata']['namespace'] = namespace
        pvc_yaml['spec']['resources']['requests']['storage'] = "4Gi"  # Update storage size if needed
        
        # Save the updated PVC YAML to a temporary file
        temp_pvc_file_name = "temp-wordpress-pvc.yaml"
        with open(temp_pvc_file_name, 'w') as temp_file:
            yaml.dump(pvc_yaml, temp_file)
        
        # Apply the PVC
        result = create_persistent_volume_claim(namespace, temp_pvc_file_name, wordpress_pvc_name)
        if result[1] != 200:
            # Return error response if PVC creation failed
            return result

        if os.path.exists(temp_pvc_file_name):
          os.remove(temp_pvc_file_name)
        file_to_remove = f"temp_{temp_pvc_file_name}"
        if os.path.exists(file_to_remove):
            os.remove(file_to_remove)
        
        # Step 4: Install Wordpress using Helm command from the db
        result = install_the_tool(tool_name)
        if result[1] != 200:
            return jsonify({"error": f"Failed to install Wordpress: {result.stderr}"}), 500
        
        output.setdefault("Wordpress", "")
        output["Wordpress"] += "Wordpress installation started successfully.\n"

        return jsonify({"message": "Wordpress installation started successfully."})
    except Exception as e:
        return jsonify({"error": f"An error occurred: {e}"}), 500
    
@app.route('/delete-wordpress', methods=['DELETE'])
def delete_wordpress():
    try:
        # Step 1: Delete the Wordpress installation using Helm
        result = uninstall_the_tool("Wordpress")
        if result[1] != 200:
            # Return error response if Wordpress uninstallation failed
            return result
        
        # Step 2: Delete the PersistentVolumeClaim (PVC) for Wordpress
        pvc_name = "data-my-wordpress"
        result = delete_persistent_volume_claim(pvc_name, "wordpress")
        if result[1] != 200:
            # Return error response if Wordpress PVC deletion failed
            return result
        
        # Step 3: Delete the PersistentVolume (PV) for Wordpress
        pv_name = "wordpress-pv"
        result = delete_pv(pv_name, "wordpress")
        if result[1] != 200:
            # Return error response if Wordpress PV deletion failed
            return result

        # Step 4: Delete the Wordpress namespace
        namespace = "wordpress"
        result = delete_namespace(namespace)
        if result[1] != 200:
            # Return error response if Wordpress namespace deletion failed
            return result
        
        return jsonify({"message": "Wordpress deletion started successfully."})
    except Exception as e:
        return jsonify({"error": f"An error occurred: {e}"}), 500

@app.route('/create-apache', methods=['GET'])
def create_apache():
    try:
        global output
        tool_name = "Apache"
        
        # Step 1: Create the namespace 'apache' if it doesn't exist
        namespace = "apache"
        result = create_namespace(namespace)
        if result[1] != 200:
            # Return error response if namespace creation failed
            return result
        
        collection = db['tools']
        apache_tool = collection.find_one({"tool_name": tool_name})
        apache_pvc_name = ""
        apache_pv_name = ""
        if apache_tool:
            apache_pvc_name = apache_tool.get("pvc_name")
            apache_pv_name = apache_tool.get("pv_name")
        else:
            return jsonify({"error": "Apache tool not found in database"}), 404
        
        print("Proceeding to create PV")
        
        # Step 2: Create the PersistentVolume (PV) for Apache
        pv_file_name = "my-custom-nfs-pv.yaml"
        with open(pv_file_name, 'r') as file:
            pv_yaml = yaml.safe_load(file)
        
        # Update PV metadata and spec for Apache
        pv_yaml['metadata']['name'] = apache_pv_name
        pv_yaml['spec']['nfs']['path'] = "/shared/nfs"  # Update the NFS path if needed
        
        # Save the updated PV YAML to a temporary file
        temp_pv_file_name = "temp-apache-pv.yaml"
        with open(temp_pv_file_name, 'w') as temp_file:
            yaml.dump(pv_yaml, temp_file)
        
        # Apply the PV
        result = create_pv(namespace, temp_pv_file_name, apache_pv_name)
        print("Result of Create PV:", result)
        if result[1] != 200:
            # Return error response if PV creation failed
            return result
        
        if os.path.exists(temp_pv_file_name):
          os.remove(temp_pv_file_name)
        file_to_remove = f"temp_{temp_pv_file_name}"
        if os.path.exists(file_to_remove):
            os.remove(file_to_remove)

        # Step 3: Create the PersistentVolumeClaim (PVC) for Apache
        pvc_file_name = "my-custom-nfs-pvc.yaml"
        with open(pvc_file_name, 'r') as file:
            pvc_yaml = yaml.safe_load(file)
        
        # Update PVC metadata and spec for Apache
        pvc_yaml['metadata']['name'] = apache_pvc_name
        pvc_yaml['metadata']['namespace'] = namespace
        pvc_yaml['spec']['resources']['requests']['storage'] = "4Gi"  # Update storage size if needed

        # Save the updated PVC YAML to a temporary file
        temp_pvc_file_name = "temp-apache-pvc.yaml"
        with open(temp_pvc_file_name, 'w') as temp_file:
            yaml.dump(pvc_yaml, temp_file)

        # Apply the PVC
        result = create_persistent_volume_claim(namespace, temp_pvc_file_name, apache_pvc_name)
        if result[1] != 200:
            # Return error response if PVC creation failed
            return result
        
        if os.path.exists(temp_pvc_file_name):
          os.remove(temp_pvc_file_name)
        file_to_remove = f"temp_{temp_pvc_file_name}"
        if os.path.exists(file_to_remove):
            os.remove(file_to_remove)
        
        # Step 4: Install Apache using Helm command from the db
        result = install_the_tool(tool_name)
        if result[1] != 200:
            return jsonify({"error": f"Failed to install Apache: {result.stderr}"}), 500

        # Step 5: Patch the Apache deployment using the patch_command from the db
        patch_command = apache_tool.get("patch_command")
        result = subprocess.run(patch_command, shell=True, capture_output=True, text=True)

        output.setdefault("Apache", "")
        output["Apache"] += "Apache installation started successfully.\n"

        return jsonify({"message": "Apache installation started successfully."})
    except Exception as e:
        return jsonify({"error": f"An error occurred: {e}"}), 500

@app.route('/delete-apache', methods=['DELETE'])
def delete_apache():
    try:
        # Step 1: Delete the Apache installation using Helm
        result = uninstall_the_tool("Apache")
        if result[1] != 200:
            # Return error response if Apache uninstallation failed
            return result
        
        # Step 2: Delete the PersistentVolumeClaim (PVC) for Apache
        pvc_name = "data-my-apache"
        result = delete_persistent_volume_claim(pvc_name, "apache")
        if result[1] != 200:
            # Return error response if Apache PVC deletion failed
            return result
        
        # Step 3: Delete the PersistentVolume (PV) for Apache
        pv_name = "apache-pv"
        result = delete_pv(pv_name, "apache")
        if result[1] != 200:
            # Return error response if Apache PV deletion failed
            return result

        # Step 4: Delete the Apache namespace
        namespace = "apache"
        result = delete_namespace(namespace)
        if result[1] != 200:
            # Return error response if Apache namespace deletion failed
            return result
        
        return jsonify({"message": "Apache deletion started successfully."})
    except Exception as e:
        return jsonify({"error": f"An error occurred: {e}"}), 500

@app.route('/create-rabbitmq', methods=['GET'])
def create_rabbitmq():
    try:
        global output
        tool_name = "RabbitMQ"
        
        # Step 1: Create the namespace 'rabbitmq' if it doesn't exist
        namespace = "rabbitmq"
        result = create_namespace(namespace)
        if result[1] != 200:
            # Return error response if namespace creation failed
            return result
        
        collection = db['tools']
        rabbitmq_tool = collection.find_one({"tool_name": tool_name})
        rabbitmq_pvc_name = ""
        rabbitmq_pv_name = ""
        if rabbitmq_tool:
            rabbitmq_pvc_name = rabbitmq_tool.get("pvc_name")
            rabbitmq_pv_name = rabbitmq_tool.get("pv_name")
        else:
            return jsonify({"error": "RabbitMQ tool not found in database"}), 404
        
        print("Proceeding to create PV")
        
        # Step 2: Create the PersistentVolume (PV) for RabbitMQ
        pv_file_name = "my-custom-nfs-pv.yaml"
        with open(pv_file_name, 'r') as file:
            pv_yaml = yaml.safe_load(file)
        
        # Update PV metadata and spec for RabbitMQ
        pv_yaml['metadata']['name'] = rabbitmq_pv_name
        pv_yaml['spec']['nfs']['path'] = "/shared/nfs"  # Update the NFS path if needed
        
        # Save the updated PV YAML to a temporary file
        temp_pv_file_name = "temp-rabbitmq-pv.yaml"
        with open(temp_pv_file_name, 'w') as temp_file:
            yaml.dump(pv_yaml, temp_file)
        
        # Apply the PV
        result = create_pv(namespace, temp_pv_file_name, rabbitmq_pv_name)
        print("Result of Create PV:", result)
        if result[1] != 200:
            # Return error response if PV creation failed
            return result

        if os.path.exists(temp_pv_file_name):
          os.remove(temp_pv_file_name)
        file_to_remove = f"temp_{temp_pv_file_name}"
        if os.path.exists(file_to_remove):
            os.remove(file_to_remove)

        # Step 3: Create the PersistentVolumeClaim (PVC) for RabbitMQ
        pvc_file_name = "my-custom-nfs-pvc.yaml"
        with open(pvc_file_name, 'r') as file:
            pvc_yaml = yaml.safe_load(file)
        
        # Update PVC metadata and spec for RabbitMQ
        pvc_yaml['metadata']['name'] = rabbitmq_pvc_name
        pvc_yaml['metadata']['namespace'] = namespace
        pvc_yaml['spec']['resources']['requests']['storage'] = "4Gi"  # Update storage size if needed
        
        # Save the updated PVC YAML to a temporary file
        temp_pvc_file_name = "temp-rabbitmq-pvc.yaml"
        with open(temp_pvc_file_name, 'w') as temp_file:
            yaml.dump(pvc_yaml, temp_file)
        
        # Apply the PVC
        result = create_persistent_volume_claim(namespace, temp_pvc_file_name, rabbitmq_pvc_name)
        if result[1] != 200:
            # Return error response if PVC creation failed
            return result
        
        if os.path.exists(temp_pvc_file_name):
          os.remove(temp_pvc_file_name)
        file_to_remove = f"temp_{temp_pvc_file_name}"
        if os.path.exists(file_to_remove):
            os.remove(file_to_remove)
        
        # Step 4: Install RabbitMQ using Helm command from the db
        result = install_the_tool(tool_name)
        if result[1] != 200:
            return jsonify({"error": f"Failed to install RabbitMQ: {result.stderr}"}), 500
        
        output.setdefault("RabbitMQ", "")
        output["RabbitMQ"] += "RabbitMQ installation started successfully.\n"

        return jsonify({"message": "RabbitMQ installation started successfully."})
    except Exception as e:
        return jsonify({"error": f"An error occurred: {e}"}), 500

@app.route('/delete-rabbitmq', methods=['DELETE'])
def delete_rabbitmq():
    try:
        # Step 1: Delete the RabbitMQ installation using Helm
        result = uninstall_the_tool("RabbitMQ")
        if result[1] != 200:
            # Return error response if RabbitMQ uninstallation failed
            return result
        
        # Step 2: Delete the PersistentVolumeClaim (PVC) for RabbitMQ
        pvc_name = "data-my-rabbitmq"
        result = delete_persistent_volume_claim(pvc_name, "rabbitmq")
        if result[1] != 200:
            # Return error response if RabbitMQ PVC deletion failed
            return result
        
        # Step 3: Delete the PersistentVolume (PV) for RabbitMQ
        pv_name = "rabbitmq-pv"
        result = delete_pv(pv_name, "rabbitmq")
        if result[1] != 200:
            # Return error response if RabbitMQ PV deletion failed
            return result

        # Step 4: Delete the RabbitMQ namespace
        namespace = "rabbitmq"
        result = delete_namespace(namespace)
        if result[1] != 200:
            # Return error response if RabbitMQ namespace deletion failed
            return result
        
        return jsonify({"message": "RabbitMQ deletion started successfully."})
    except Exception as e:
        return jsonify({"error": f"An error occurred: {e}"}), 500

@app.route('/create-argocd', methods=['GET'])
def create_argocd():
    try:
        global output
        tool_name = "ArgoCD"
        print(f"Starting Argo CD installation for tool: {tool_name}")

        # Step 1: Create the namespace 'argocd' if it doesn't exist
        namespace = "argocd"
        print(f"Creating namespace: {namespace}")
        result = create_namespace(namespace)
        if result[1] != 200:
            print(f"Namespace creation failed: {result[0].data}")
            return result
        
        collection = db['tools']
        print(f"Fetching Argo CD tool details from the database")
        argocd_tool = collection.find_one({"tool_name": tool_name})
        argocd_pvc_name = ""
        argocd_pv_name = ""
        if argocd_tool:
            argocd_pvc_name = argocd_tool.get("pvc_name")
            argocd_pv_name = argocd_tool.get("pv_name")
            print(f"Found Argo CD tool in database: PVC={argocd_pvc_name}, PV={argocd_pv_name}")
        else:
            print("Argo CD tool not found in database")
            return jsonify({"error": "Argo CD tool not found in database"}), 404
        
        print("Proceeding to create PV")
        
        # Step 2.1: Create the PersistentVolume (PV) for Argo CD
        pv_file_name = "my-custom-nfs-pv.yaml"
        with open(pv_file_name, 'r') as file:
            pv_yaml = yaml.safe_load(file)
        
        # Update PV metadata and spec for Argo CD
        pv_yaml['metadata']['name'] = argocd_pv_name
        pv_yaml['spec']['nfs']['path'] = "/shared/nfs"  # Update the NFS path if needed
        
        # Save the updated PV YAML to a temporary file
        temp_pv_file_name = "temp-argocd-pv.yaml"
        with open(temp_pv_file_name, 'w') as temp_file:
            yaml.dump(pv_yaml, temp_file)
        
        # Apply the PV
        print(f"Applying PV YAML: {temp_pv_file_name}")
        result = create_pv(namespace, temp_pv_file_name, argocd_pv_name)
        print("Result of Create PV:", result)
        if result[1] != 200:
            print(f"PV creation failed: {result[0].data}")
            return result
        
        if os.path.exists(temp_pv_file_name):
          os.remove(temp_pv_file_name)
        file_to_remove = f"temp_{temp_pv_file_name}"
        if os.path.exists(file_to_remove):
            os.remove(file_to_remove)

        # Step 2.2: Create the PersistentVolume (PV) for Argo CD Redis
        pv_file_name = "my-custom-nfs-pv.yaml"
        with open(pv_file_name, 'r') as file:
            pv_yaml = yaml.safe_load(file)
        
        # Update PV metadata and spec for Argo CD Redis
        pv_yaml['metadata']['name'] = "redis-pv"
        pv_yaml['spec']['nfs']['path'] = "/shared/nfs"  # Update the NFS path if needed
        
        # Save the updated PV YAML to a temporary file
        temp_pv_file_name = "temp-argocd-redis-pv.yaml"
        with open(temp_pv_file_name, 'w') as temp_file:
            yaml.dump(pv_yaml, temp_file)
        
        # Apply the PV
        print(f"Applying Redis PV YAML: {temp_pv_file_name}")
        result = create_pv(namespace, temp_pv_file_name, "redis-pv")
        print("Result of Create Redis PV:", result)
        if result[1] != 200:
            print(f"Redis PV creation failed: {result[0].data}")
            return result

        if os.path.exists(temp_pv_file_name):
          os.remove(temp_pv_file_name)
        file_to_remove = f"temp_{temp_pv_file_name}"
        if os.path.exists(file_to_remove):
            os.remove(file_to_remove)

        # Step 3.1: Create the PersistentVolumeClaim (PVC) for Argo CD
        pvc_file_name = "my-custom-nfs-pvc.yaml"
        with open(pvc_file_name, 'r') as file:
            pvc_yaml = yaml.safe_load(file)
        
        # Update PVC metadata and spec for Argo CD
        pvc_yaml['metadata']['name'] = argocd_pvc_name
        pvc_yaml['metadata']['namespace'] = namespace
        pvc_yaml['spec']['resources']['requests']['storage'] = "4Gi"  # Update storage size if needed
        
        # Save the updated PVC YAML to a temporary file
        temp_pvc_file_name = "temp-argocd-pvc.yaml"
        with open(temp_pvc_file_name, 'w') as temp_file:
            yaml.dump(pvc_yaml, temp_file)
        
        # Apply the PVC
        print(f"Applying PVC YAML: {temp_pvc_file_name}")
        result = create_persistent_volume_claim(namespace, temp_pvc_file_name, argocd_pvc_name)
        if result[1] != 200:
            print(f"PVC creation failed: {result[0].data}")
            return result
        
        if os.path.exists(temp_pvc_file_name):
          os.remove(temp_pvc_file_name)
        file_to_remove = f"temp_{temp_pvc_file_name}"
        if os.path.exists(file_to_remove):
            os.remove(file_to_remove)
        
        # Step 3.2: Create the PersistentVolumeClaim (PVC) for Argo CD Redis
        pvc_file_name = "my-custom-nfs-pvc.yaml"
        with open(pvc_file_name, 'r') as file:
            pvc_yaml = yaml.safe_load(file)
        
        # Update PVC metadata and spec for Argo CD Redis
        pvc_yaml['metadata']['name'] = "redis-data-argocd-redis-master-0"
        pvc_yaml['metadata']['namespace'] = namespace
        pvc_yaml['spec']['resources']['requests']['storage'] = "4Gi"  # Update storage size if needed
        
        # Save the updated PVC YAML to a temporary file
        temp_pvc_file_name = "temp-argocd-redis-pvc.yaml"
        with open(temp_pvc_file_name, 'w') as temp_file:
            yaml.dump(pvc_yaml, temp_file)
        
        # Apply the PVC
        print(f"Applying Redis PVC YAML: {temp_pvc_file_name}")
        result = create_persistent_volume_claim(namespace, temp_pvc_file_name, "redis-data-argocd-redis-master-0")
        if result[1] != 200:
            print(f"Redis PVC creation failed: {result[0].data}")
            return result
        
        if os.path.exists(temp_pvc_file_name):
          os.remove(temp_pvc_file_name)
        file_to_remove = f"temp_{temp_pvc_file_name}"
        if os.path.exists(file_to_remove):
            os.remove(file_to_remove)
        
        # Step 4: Install Argo CD using Helm command from the db
        print("Installing Argo CD using Helm")
        result = install_the_tool(tool_name)
        if result[1] != 200:
            print(f"Helm installation failed: {result.stderr}")
            return jsonify({"error": f"Failed to install Argo CD: {result.stderr}"}), 500
        
        # Step 5: Disable authentication in Argo CD
        def disable_argocd_authentication(namespace):
          # Patch the argocd-cm ConfigMap to allow anonymous access
          patch_command = (
              f"kubectl patch configmap argocd-cm -n {namespace} --type merge -p "
              "'{\"data\":{\"users.anonymous.enabled\":\"true\"}}'"
          )
          subprocess.run(patch_command, shell=True, check=True)

          # Restart the Argo CD server pod to apply the changes
          restart_command = (
              f"kubectl rollout restart deployment argocd-argo-cd-server -n {namespace}"
          )
          subprocess.run(restart_command, shell=True, check=True)

        print("Disabling authentication in Argo CD")

        disable_argocd_authentication(namespace)

        output.setdefault("ArgoCD", "")
        output["ArgoCD"] += "Argo CD installation started successfully.\n"

        print("Argo CD installation completed successfully")
        return jsonify({"message": "Argo CD installation started successfully."}), 200
    except Exception as e:
        import traceback
        print(f"An error occurred: {e}")
        print(traceback.format_exc())
        return jsonify({"error": f"An error occurred: {e}"}), 500
  
@app.route('/delete-argocd', methods=['DELETE'])
def delete_argocd():
    try:
        # Step 1: Delete the RabbitMQ installation using Helm
        result = uninstall_the_tool("ArgoCD")
        if result[1] != 200:
            # Return error response if RabbitMQ uninstallation failed
            return result
        
        # Step 2.1: Delete the PersistentVolumeClaim (PVC) for RabbitMQ
        pvc_name = "data-my-argocd"
        result = delete_persistent_volume_claim(pvc_name, "argocd")
        if result[1] != 200:
            # Return error response if RabbitMQ PVC deletion failed
            return result
        # Step 2.2: Delete the PersistentVolumeClaim (PVC) for RabbitMQ
        pvc_name = "redis-data-argocd-redis-master-0"
        result = delete_persistent_volume_claim(pvc_name, "argocd")
        if result[1] != 200:
            # Return error response if RabbitMQ PVC deletion failed
            return result

        # Step 3.1: Delete the PersistentVolume (PV) for RabbitMQ
        pv_name = "argocd-pv"
        result = delete_pv(pv_name, "argocd")
        if result[1] != 200:
            # Return error response if RabbitMQ PV deletion failed
            return result
        
        # Step 3.2: Delete the PersistentVolume (PV) for RabbitMQ
        pv_name = "redis-pv"
        result = delete_pv(pv_name, "argocd")
        if result[1] != 200:
            # Return error response if RabbitMQ PV deletion failed
            return result

        # Step 4: Delete the RabbitMQ namespace
        namespace = "argocd"
        result = delete_namespace(namespace)
        if result[1] != 200:
            # Return error response if RabbitMQ namespace deletion failed
            return result
        
        return jsonify({"message": "ArgoCD deletion started successfully."})
    except Exception as e:
        return jsonify({"error": f"An error occurred: {e}"}), 500

@app.route('/create-jenkins', methods=['GET'])
def create_jenkins():
    try:
        global output
        tool_name = "Jenkins"
        print(f"Starting Jenkins installation for tool: {tool_name}")

        # Step 1: Create the namespace 'jenkins' if it doesn't exist
        namespace = "jenkins"
        print(f"Creating namespace: {namespace}")
        result = create_namespace(namespace)
        if result[1] != 200:
            print(f"Namespace creation failed: {result[0].data}")
            return result
        
        # Step 2: Fetch Jenkins tool details from the database
        collection = db['tools']
        print(f"Fetching Jenkins tool details from the database")
        jenkins_tool = collection.find_one({"tool_name": tool_name})
        jenkins_pvc_name = ""
        jenkins_pv_name = ""
        if jenkins_tool:
            jenkins_pvc_name = jenkins_tool.get("pvc_name")
            jenkins_pv_name = jenkins_tool.get("pv_name")
            print(f"Found Jenkins tool in database: PVC={jenkins_pvc_name}, PV={jenkins_pv_name}")
        else:
            print("Jenkins tool not found in database")
            return jsonify({"error": "Jenkins tool not found in database"}), 404
        
        # Step 3: Create the PersistentVolume (PV) for Jenkins
        print("Proceeding to create PersistentVolume (PV)")
        pv_file_name = "my-custom-nfs-pv.yaml"
        with open(pv_file_name, 'r') as file:
            pv_yaml = yaml.safe_load(file)
        
        # Update PV metadata and spec for Jenkins
        pv_yaml['metadata']['name'] = jenkins_pv_name
        pv_yaml['spec']['nfs']['path'] = "/shared/nfs"  # Update the NFS path if needed
        
        # Save the updated PV YAML to a temporary file
        temp_pv_file_name = "temp-jenkins-pv.yaml"
        with open(temp_pv_file_name, 'w') as temp_file:
            yaml.dump(pv_yaml, temp_file)
        
        # Apply the PV
        print(f"Applying PV YAML: {temp_pv_file_name}")
        result = create_pv(namespace, temp_pv_file_name, jenkins_pv_name)
        print("Result of Create PV:", result)
        if result[1] != 200:
            print(f"PV creation failed: {result[0].data}")
            return result
        
        if os.path.exists(temp_pv_file_name):
          os.remove(temp_pv_file_name)
        file_to_remove = f"temp_{temp_pv_file_name}"
        if os.path.exists(file_to_remove):
            os.remove(file_to_remove)

        # Step 4: Create the PersistentVolumeClaim (PVC) for Jenkins
        print("Proceeding to create PersistentVolumeClaim (PVC)")
        pvc_file_name = "my-custom-nfs-pvc.yaml"
        with open(pvc_file_name, 'r') as file:
            pvc_yaml = yaml.safe_load(file)
        
        # Update PVC metadata and spec for Jenkins
        pvc_yaml['metadata']['name'] = jenkins_pvc_name
        pvc_yaml['metadata']['namespace'] = namespace
        pvc_yaml['spec']['resources']['requests']['storage'] = "4Gi"  # Update storage size if needed
        
        # Save the updated PVC YAML to a temporary file
        temp_pvc_file_name = "temp-jenkins-pvc.yaml"
        with open(temp_pvc_file_name, 'w') as temp_file:
            yaml.dump(pvc_yaml, temp_file)
        
        # Apply the PVC
        print(f"Applying PVC YAML: {temp_pvc_file_name}")
        result = create_persistent_volume_claim(namespace, temp_pvc_file_name, jenkins_pvc_name)
        if result[1] != 200:
            print(f"PVC creation failed: {result[0].data}")
            return result
        
        if os.path.exists(temp_pvc_file_name):
          os.remove(temp_pvc_file_name)
        file_to_remove = f"temp_{temp_pvc_file_name}"
        if os.path.exists(file_to_remove):
            os.remove(file_to_remove)
        
        # Step 5: Install Jenkins using Helm command from the db
        print("Installing Jenkins using Helm")
        result = install_the_tool(tool_name)
        if result[1] != 200:
            print(f"Helm installation failed: {result.stderr}")
            return jsonify({"error": f"Failed to install Jenkins: {result.stderr}"}), 500
        
        # Step 6: Wait for the Jenkins pod to be running
        print("Waiting for Jenkins pod to be running")
        def wait_for_pod_running(namespace, pod_name_prefix, timeout=300):
          import time
          import subprocess
          start_time = time.time()
          while time.time() - start_time < timeout:
              # Get the pod status using kubectl, grep, and awk
              pod_status = subprocess.run(
                  ["kubectl", "get", "pods", "-n", namespace, "--no-headers", "-o", "custom-columns=:metadata.name,:status.phase"],
                  capture_output=True, text=True
              )
              
              if pod_status.returncode != 0:
                  print(f"Error checking pod status: {pod_status.stderr}")
                  return False
              
              # Parse the output to find the pod with the matching prefix
              for line in pod_status.stdout.splitlines():
                  pod_name, status = line.split()
                  if pod_name.startswith(pod_name_prefix):
                      print(f"Pod {pod_name} status: {status}")
                      if status == "Running":
                          print("Jenkins pod is running")
                          return True
                      break
              
              time.sleep(5)
          
          print("Jenkins pod did not start within the expected time")
          return False

        if not wait_for_pod_running(namespace, "jenkins"):
            return jsonify({"error": "Jenkins pod did not start within the expected time"}), 500

        # Step 7: Disable security by updating the config.xml file
        print("Disabling Jenkins security")
        
        def disable_jenkins_security(namespace, pod_name_prefix):
          import subprocess
          import os

          # Get the Jenkins pod name
          pod_name_output = subprocess.run(
              ["kubectl", "get", "pods", "-n", namespace, "--no-headers", "-o", "custom-columns=:metadata.name"],
              capture_output=True, text=True
          )

          if pod_name_output.returncode != 0:
              print(f"Error getting pod name: {pod_name_output.stderr}")
              raise Exception("Failed to get Jenkins pod name")

          # Find the pod with the matching prefix
          pod_name = None
          for line in pod_name_output.stdout.splitlines():
              if line.startswith(pod_name_prefix):
                  pod_name = line
                  break

          if not pod_name:
              print(f"No pod found with prefix: {pod_name_prefix}")
              raise Exception("Jenkins pod not found")

          print(f"Jenkins pod name: {pod_name}")

          # Generate the config.xml file locally
          config_xml_path = "/tmp/config.xml"
          config_xml_content = """<?xml version="1.1" encoding="UTF-8"?>
      <hudson>
        <disabledAdministrativeMonitors/>
        <version>2.492.2</version>
        <numExecutors>2</numExecutors>
        <mode>NORMAL</mode>
        <useSecurity>false</useSecurity>
        <securityRealm class="hudson.security.HudsonPrivateSecurityRealm">
          <disableSignup>true</disableSignup>
          <enableCaptcha>false</enableCaptcha>
        </securityRealm>
        <disableRememberMe>false</disableRememberMe>
        <projectNamingStrategy class="jenkins.model.ProjectNamingStrategy$DefaultProjectNamingStrategy"/>
        <workspaceDir>${JENKINS_HOME}/workspace/${ITEM_FULL_NAME}</workspaceDir>
        <buildsDir>${ITEM_ROOTDIR}/builds</buildsDir>
        <jdks/>
        <viewsTabBar class="hudson.views.DefaultViewsTabBar"/>
        <myViewsTabBar class="hudson.views.DefaultMyViewsTabBar"/>
        <clouds/>
        <scmCheckoutRetryCount>0</scmCheckoutRetryCount>
        <views>
          <hudson.model.AllView>
            <owner class="hudson" reference="../../.."/>
            <name>all</name>
            <filterExecutors>false</filterExecutors>
            <filterQueue>false</filterQueue>
            <properties class="hudson.model.View$PropertyList"/>
          </hudson.model.AllView>
        </views>
        <primaryView>all</primaryView>
        <slaveAgentPort>-1</slaveAgentPort>
        <label></label>
        <crumbIssuer class="hudson.security.csrf.DefaultCrumbIssuer">
          <excludeClientIPFromCrumb>true</excludeClientIPFromCrumb>
        </crumbIssuer>
        <nodeProperties/>
        <globalNodeProperties/>
        <nodeRenameMigrationNeeded>false</nodeRenameMigrationNeeded>
      </hudson>
      """
          with open(config_xml_path, "w") as f:
              f.write(config_xml_content)

          print(f"config.xml file written to {config_xml_path}")

          # Copy the config.xml file into the Jenkins pod
          print("Copying config.xml to Jenkins pod")
          subprocess.run(
              ["kubectl", "cp", config_xml_path, f"{namespace}/{pod_name}:/bitnami/jenkins/home/config.xml"],
              check=True
          )

          # Restart the Jenkins pod to apply the changes
          print("Restarting Jenkins pod")
          subprocess.run(
              ["kubectl", "delete", "pod", "-n", namespace, pod_name],
              check=True
          )

          # Clean up the local config.xml file
          os.remove(config_xml_path)
          print("Local config.xml file removed")
        
        disable_jenkins_security(namespace, "jenkins")

        output.setdefault("Jenkins", "")
        output["Jenkins"] += "Jenkins installation started successfully.\n"

        print("Jenkins installation completed successfully")
        return jsonify({"message": "Jenkins installation started successfully."}), 200
    except Exception as e:
        import traceback
        print(f"An error occurred: {e}")
        print(traceback.format_exc())
        return jsonify({"error": f"An error occurred: {e}"}), 500

@app.route('/delete-jenkins', methods=['DELETE'])
def delete_jenkins():
    try:
        # Step 1: Delete the Jenkins installation using Helm
        result = uninstall_the_tool("Jenkins")
        if result[1] != 200:
            # Return error response if Jenkins uninstallation failed
            return result
        
        # Step 2: Delete the PersistentVolumeClaim (PVC) for Jenkins
        pvc_name = "data-my-jenkins"
        result = delete_persistent_volume_claim(pvc_name, "jenkins")
        if result[1] != 200:
            # Return error response if Jenkins PVC deletion failed
            return result
        
        # Step 3: Delete the PersistentVolume (PV) for Jenkins
        pv_name = "jenkins-pv"
        result = delete_pv(pv_name, "jenkins")
        if result[1] != 200:
            # Return error response if Jenkins PV deletion failed
            return result

        # Step 4: Delete the Jenkins namespace
        namespace = "jenkins"
        result = delete_namespace(namespace)
        if result[1] != 200:
            # Return error response if Jenkins namespace deletion failed
            return result
        
        return jsonify({"message": "Jenkins deletion started successfully."})
    except Exception as e:
        return jsonify({"error": f"An error occurred: {e}"}), 500

@app.route('/create-zipkin', methods=['GET'])
def create_zipkin():
    try:
        global output
        tool_name = "Zipkin"
        
        # Step 1: Create the namespace 'zipkin' if it doesn't exist
        namespace = "zipkin"
        result = create_namespace(namespace)
        if result[1] != 200:
            # Return error response if namespace creation failed
            return result
        
        collection = db['tools']
        zipkin_tool = collection.find_one({"tool_name": tool_name})
        zipkin_pvc_name = ""
        zipkin_pv_name = ""
        if zipkin_tool:
            zipkin_pvc_name = zipkin_tool.get("pvc_name")
            zipkin_pv_name = zipkin_tool.get("pv_name")
        else:
            return jsonify({"error": "Zipkin tool not found in database"}), 404
        
        print("Proceeding to create PV")
        
        # Step 2.1: Create the PersistentVolume (PV) for Zipkin
        pv_file_name = "my-custom-nfs-pv.yaml"
        with open(pv_file_name, 'r') as file:
            pv_yaml = yaml.safe_load(file)
        
        # Update PV metadata and spec for Zipkin
        pv_yaml['metadata']['name'] = zipkin_pv_name
        pv_yaml['spec']['nfs']['path'] = "/shared/nfs"  # Update the NFS path if needed
        
        # Save the updated PV YAML to a temporary file
        temp_pv_file_name = "temp-zipkin-pv.yaml"
        with open(temp_pv_file_name, 'w') as temp_file:
            yaml.dump(pv_yaml, temp_file)
        
        # Apply the PV
        result = create_pv(namespace, temp_pv_file_name, zipkin_pv_name)
        print("Result of Create PV:", result)
        if result[1] != 200:
            # Return error response if PV creation failed
            return result

        # Step 2.2: Create the PersistentVolume (PV) for Zipkin
        pv_file_name = "my-custom-nfs-pv.yaml"
        with open(pv_file_name, 'r') as file:
            pv_yaml = yaml.safe_load(file)
        
        # Update PV metadata and spec for Zipkin
        pv_yaml['metadata']['name'] = "zipkin-cassandra-pv"
        pv_yaml['spec']['nfs']['path'] = "/shared/nfs"  # Update the NFS path if needed
        
        # Save the updated PV YAML to a temporary file
        temp_pv_file_name = "temp-zipkin-cassandra-pv.yaml"
        with open(temp_pv_file_name, 'w') as temp_file:
            yaml.dump(pv_yaml, temp_file)
        
        # Apply the PV
        result = create_pv(namespace, temp_pv_file_name, "zipkin-cassandra-pv")
        print("Result of Create PV:", result)
        if result[1] != 200:
            # Return error response if PV creation failed
            return result

        # Step 3: Create the PersistentVolumeClaim (PVC) for Zipkin
        pvc_file_name = "my-custom-nfs-pvc.yaml"
        with open(pvc_file_name, 'r') as file:
            pvc_yaml = yaml.safe_load(file)
        
        # Update PVC metadata and spec for Zipkin
        pvc_yaml['metadata']['name'] = zipkin_pvc_name
        pvc_yaml['metadata']['namespace'] = namespace
        pvc_yaml['spec']['resources']['requests']['storage'] = "4Gi"  # Update storage size if needed
        
        # Save the updated PVC YAML to a temporary file
        temp_pvc_file_name = "temp-zipkin-pvc.yaml"
        with open(temp_pvc_file_name, 'w') as temp_file:
            yaml.dump(pvc_yaml, temp_file)
        
        # Apply the PVC
        result = create_persistent_volume_claim(namespace, temp_pvc_file_name, zipkin_pvc_name)
        if result[1] != 200:
            # Return error response if PVC creation failed
            return result
        
        # Step 4: Install Zipkin using Helm command from the db
        result = install_the_tool(tool_name)
        if result[1] != 200:
            return jsonify({"error": f"Failed to install Zipkin: {result.stderr}"}), 500

        output.setdefault("Zipkin", "")
        output["Zipkin"] += "Zipkin installation started successfully.\n"

        return jsonify({"message": "Zipkin installation started successfully."})
    except Exception as e:
        return jsonify({"error": f"An error occurred: {e}"}), 500

@app.route('/delete-zipkin', methods=['DELETE'])
def delete_zipkin():
    try:
        # Step 1: Delete the Zipkin installation using Helm
        result = uninstall_the_tool("Zipkin")
        if result[1] != 200:
            # Return error response if Zipkin uninstallation failed
            return result
        
        # Step 2: Delete the PersistentVolumeClaim (PVC) for Zipkin
        pvc_name = "data-my-zipkin"
        result = delete_persistent_volume_claim(pvc_name, "zipkin")
        if result[1] != 200:
            # Return error response if Zipkin PVC deletion failed
            return result

        # Step 2: Delete the PersistentVolumeClaim (PVC) for Zipkin
        pvc_name = "data-zipkin-cassandra-0"
        result = delete_persistent_volume_claim(pvc_name, "zipkin")
        if result[1] != 200:
            # Return error response if Zipkin PVC deletion failed
            return result
        
        # Step 3: Delete the PersistentVolume (PV) for Zipkin
        pv_name = "zipkin-pv"
        result = delete_pv(pv_name, "zipkin")
        if result[1] != 200:
            # Return error response if Zipkin PV deletion failed
            return result
        
        # Step 3: Delete the PersistentVolume (PV) for Zipkin
        pv_name = "zipkin-cassandra-pv"
        result = delete_pv(pv_name, "zipkin")
        if result[1] != 200:
            # Return error response if Zipkin PV deletion failed
            return result

        # Step 4: Delete the Zipkin namespace
        namespace = "zipkin"
        result = delete_namespace(namespace)
        if result[1] != 200:
            # Return error response if Zipkin namespace deletion failed
            return result
        
        return jsonify({"message": "Zipkin deletion started successfully."})
    except Exception as e:
        return jsonify({"error": f"An error occurred: {e}"}), 500

@app.route('/count-pods/<namespace>', methods=['GET'])
def count_running_pods(namespace):
    pods = get_pods_in_namespace(namespace)
    total_pods = len(pods)
    running_pods = sum(1 for pod in pods if pod["status"] == "Running")
    return f"{running_pods}/{total_pods}"
 
@app.route('/get-pods/<namespace>', methods=['GET'])
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


@app.route('/get-service-port/<namespace>/<service>', methods=['GET'])
def get_service_port(namespace, service):
    try:
        # Load Kubernetes configuration from default location
       

        # Create a Kubernetes API client
        v1 = client.CoreV1Api()

        # Define the service name
        service_name = service

        # Get the service details
        service = v1.read_namespaced_service(service_name, namespace)

        # Get the NodePort
        node_port = service.spec.ports[0].node_port

        return {"namespace": namespace, "service_name": service_name, "node_port": node_port}

    except Exception as e:
        return {"error": str(e)}

@app.route('/get-proxy/<namespace>', methods=['GET'])
def get_proxy_public_node_port(namespace):
    try:
        # Load Kubernetes configuration from default location
       

        # Create a Kubernetes API client
        v1 = client.CoreV1Api()

        # Define the service name
        service_name = "proxy-public"

        # Get the service details
        service = v1.read_namespaced_service(service_name, namespace)

        # Get the NodePort
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

def pod_exec(name, namespace, command,tool_name):
    global output
    print("POD EXEC CALLED")
    # Load kubeconfig file
    config.load_kube_config()

    # Create the API client
    api_instance = client.CoreV1Api()
    # print("API INSTANCE CREATED:", api_instance)
    exec_command = ["/bin/sh", "-c", command]
    print("EXEC COMMAND:", exec_command)
    response = api_instance.read_namespaced_pod(name=name,
                                                namespace=namespace)
    resp = stream(api_instance.connect_get_namespaced_pod_exec,
                  name,
                  namespace,
                  command=exec_command,
                  stderr=True, stdin=False,
                  stdout=True, tty=False,
                  _preload_content=False)
    output.setdefault(tool_name, "")
    output[tool_name] = ""
    while resp.is_open():
        resp.update(timeout=1)
        stdout = resp.read_stdout() or ""
        stderr = resp.read_stderr() or ""
        output[tool_name] += f"STDOUT: {stdout}\nSTDERR: {stderr}\n"

@app.route('/execute-command')
def execute_command(command,tool_name):
    global output

    # Get the current node's name
    
    update_current_node()
    if current_node:
        # Define the command to run
        

        # Execute the pod_exec function in a background thread
        thread = threading.Thread(target=pod_exec, args=(current_node, "default", command,tool_name))
        thread.start()

        return jsonify({"message": "Command execution started."})
    else:
        return jsonify({"error": "Current node not found."})



@app.route('/execute-commands', methods=['POST'])
def execute_commands():
    data = request.json
    command = data.get('command')
    namespace = data.get('namespace', 'default') 
    update_current_node() # Use 'default' namespace if not specified
    pod_name = current_node
    print(pod_name)
  
    if not command or not pod_name:
        return jsonify({"message": "Command and pod_name are required"}), 400

    try:
        # Create an API client

        config.load_kube_config()

    # Create the API client
   
        api_instance = client.CoreV1Api()

        # Execute the command on the pod
        exec_command = ['/bin/sh', '-c', command]
        resp = stream(api_instance.connect_get_namespaced_pod_exec,
                      pod_name,
                      namespace,
                      command=exec_command,
                      stderr=True, stdin=False,
                      stdout=True, tty=False)
        message = resp
    except client.rest.ApiException as e:
        print(e)
        message = f"Exception when calling CoreV1Api->connect_get_namespaced_pod_exec: {e}"
    print(message)
    return jsonify({"message": message})



@app.route('/get-status/<tool_name>', methods=['GET'])
def get_status(tool_name):
    global output
    if tool_name in output:
        return jsonify({"status": output[tool_name]})
    else:
        return jsonify({"error": f"Status for {tool_name} not found."})


@app.route('/delete-all-pvs', methods=['DELETE'])
def delete_all_pvs():
    try:
        k8s= client.CoreV1Api()
        # Get all PersistentVolumes
        pvs = k8s.list_persistent_volume().items

        deleted_pvs = []
        for pv in pvs:
            # Check if PV status is "Available" or "Released"
            if pv.status.phase in [ "Available","Released"]:
                # Delete the PV
                try:
                    k8s.delete_persistent_volume(pv.metadata.name, body=client.V1DeleteOptions())
                    deleted_pvs.append(pv.metadata.name)
                except ApiException as e:
                    return jsonify({"error": f"Error deleting PV '{pv.metadata.name}': {e}"}), 500

        return jsonify({"message": f"Deleted PVs: {deleted_pvs}"}), 200

    except ApiException as e:
        return jsonify({"error": f"Kubernetes API error: {e.reason}"}), 500
    except Exception as e:
        return jsonify({"error": f"An error occurred: {e}"}), 500

@app.route('/installtool/<tool_name>', methods=['GET'])
def install_tool(tool_name):
    if tool_name == "JupyterHub":
        return create_jupyterhub()
    elif tool_name == "BinderHub":
        
        return create_binderhub()
    elif tool_name == "Prometheus":
        
        return create_prometheus()
    elif tool_name == "Grafana":
        
        return create_grafana()
    elif tool_name == "MariaDB":
        
        return create_mariadb()
    elif tool_name == "Wordpress":
        
        return create_wordpress()
    elif tool_name == "Apache":
        
        return create_apache()
    elif tool_name == "RabbitMQ":
        
        return create_rabbitmq()
    elif tool_name == "ArgoCD":
        
        return create_argocd()
    elif tool_name == "Jenkins":
        
        return create_jenkins()
    elif tool_name == "Zipkin":

        return create_zipkin()
    else:
        return jsonify({"error": f"Installation for {tool_name} not implemented."}), 404


#Tool Queue management 
class ToolQueue:
    def __init__(self, tool_id, queue_limit, queue=None, waiting_queue=None):
        self.tool_id = tool_id
        self.queue_limit = queue_limit
        self.queue = queue if queue else []
        self.waiting_queue = waiting_queue if waiting_queue else []

    def to_dict(self):
        return {
            "tool_id": self.tool_id,
            "queue_limit": self.queue_limit,
            "queue": self.queue,
            "waiting_queue": self.waiting_queue
        }


@app.route('/add-tools-to-queue', methods=['GET'])
def add_tools_to_queue():
    try:
        # Accessing the 'tools' collection
        collection = db['tools']

        # Fetch all tools from the collection
        tools = collection.find({}, {"_id": 1})

        # Extract tool IDs from the tools
        tool_ids = [tool["_id"] for tool in tools]

        # Accessing the 'toolQueue' collection
        tool_queue_collection = db['toolQueue']

        # Add tool IDs to the tool queue with default values
        for tool_id in tool_ids:
            tool_queue_collection.insert_one({
                "tool_id": tool_id,
                "waiting_queue": [],
                "queue": [],
                "queue_limit": 0
            })

        return jsonify({"message": "Tools added to the queue successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


from bson import ObjectId

@app.route('/set-queue-limit', methods=['POST'])
def set_queue_limit():
    try:
        # Extract data from the POST request
        data = request.json
        tool_id_str = data.get('tool_id')
        tool_id = ObjectId(tool_id_str)  # Convert string to ObjectId
        print(tool_id)
        queue_limit = data.get('queue_limit')

        # Accessing the 'toolQueue' collection
        tool_queue_collection = db['toolQueue']
        tool_info = tool_queue_collection.find_one({"tool_id": tool_id})  # Use '_id' instead of 'tool_id'
      
        if tool_info is None:
            return jsonify({"error": "Tool not found"}), 404

        # Update the queue limit for the specified tool
        tool_queue_collection.update_one(
            {"tool_id": tool_id},
            {"$set": {"queue_limit": int(queue_limit)}}
        )

        return jsonify({"message": f"Queue limit set to {queue_limit} for tool {tool_id_str}"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get-queue-limit/<tool_id>', methods=['GET'])
def get_queue_limit(tool_id):
    try:
        # Convert string to ObjectId
        tool_id = ObjectId(tool_id)
        
        # Accessing the 'toolQueue' collection
        tool_queue_collection = db['toolQueue']
        
        # Find the tool with the specified tool_id
        tool_info = tool_queue_collection.find_one({"tool_id": tool_id})
        
        if tool_info is None:
            return jsonify({"error": "Tool not found"}), 404
        
        # Extract the queue limit from the tool info
        queue_limit = tool_info.get('queue_limit')
        
        return jsonify({"tool_id": str(tool_id), "queue_limit": queue_limit}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/add-to-waiting-list', methods=['POST'])
def add_to_waiting_list():
    try:
        # Extract data from the POST request
        data = request.json
        user_id = data.get('user_id')
        tool_id_str = data.get('tool_id')
        tool_id = ObjectId(tool_id_str)  # Convert string to ObjectId

        # Accessing the 'toolQueue' collection
        tool_queue_collection = db['toolQueue']
        tool_info = tool_queue_collection.find_one({"tool_id": tool_id})

        if tool_info is None:
            return jsonify({"error": "Tool not found"}), 404

        # Check if user is already in the waiting list
        if user_id in tool_info.get('waiting_queue', []):
            return jsonify({"message": f"User {user_id} is already in the waiting list for tool {tool_id_str}"}), 200

        # Add user to the waiting list for the specified tool
        tool_queue_collection.update_one(
            {"tool_id": tool_id},
            {"$push": {"waiting_queue": user_id}}
        )

        return jsonify({"message": f"User {user_id} added to waiting list for tool {tool_id_str}"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

#remove from waiting list
from flask import request, jsonify

@app.route('/remove-from-waiting-list', methods=['POST'])
def remove_from_waiting_list():
    try:
        # Extract data from the POST request
        data = request.json
        user_id = data.get('user_id')
        tool_id_str = data.get('tool_id')
        tool_id = ObjectId(tool_id_str)  # Convert string to ObjectId

        # Accessing the 'toolQueue' collection
        tool_queue_collection = db['toolQueue']
        tool_info = tool_queue_collection.find_one({"tool_id": tool_id})

        if tool_info is None:
            return jsonify({"error": "Tool not found"}), 404

        # Check if user is in the waiting list
        if user_id not in tool_info.get('waiting_queue', []):
            return jsonify({"message": f"User {user_id} is not in the waiting list for tool {tool_id_str}"}), 200

        # Remove user from the waiting list for the specified tool
        tool_queue_collection.update_one(
            {"tool_id": tool_id},
            {"$pull": {"waiting_queue": user_id}}
        )

        return jsonify({"message": f"User {user_id} removed from waiting list for tool {tool_id_str}"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/waiting-list', methods=['POST'])
def get_waiting_list():
    try:
        # Extract tool_id from the query parameters
        data = request.json
        tool_id_str = data.get('tool_id')
        tool_id = ObjectId(tool_id_str)  # Convert string to ObjectId

        # Accessing the 'toolQueue' collection
        tool_queue_collection = db['toolQueue']
        tool_info = tool_queue_collection.find_one({"tool_id": tool_id})

        if tool_info is None:
            return jsonify({"error": "Tool not found"}), 404

        # Get the waiting list for the specified tool
        waiting_list = tool_info.get('waiting_queue', [])
        roles_collection = db['roles']

        # Fetch usernames based on queue_ids
        queue_users = []
        for user_id in waiting_list:
            user_info = roles_collection.find_one({"_id": ObjectId(user_id)}, {"username": 1, "_id": 0})
            if user_info:
                queue_users.append(user_info['username'])
        return jsonify({"waiting_list": queue_users}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/queue', methods=['POST'])
def get_queue():
    try:
        # Extract data from the POST request
        data = request.json
        tool_id_str = data.get('tool_id')
        tool_id = ObjectId(tool_id_str)  # Convert string to ObjectId

        # Accessing the 'toolQueue' collection
        tool_queue_collection = db['toolQueue']
        tool_info = tool_queue_collection.find_one({"tool_id": tool_id})

        if tool_info is None:
            return jsonify({"error": "Tool not found"}), 404

        # Get the current queue for the specified tool
        queue_ids = tool_info.get('queue', [])

        # Accessing the 'roles' collection
        roles_collection = db['roles']

        # Fetch usernames based on queue_ids
        queue_users = []
        for user_id in queue_ids:
            user_info = roles_collection.find_one({"_id": ObjectId(user_id)}, {"username": 1, "_id": 0})
            if user_info:
                queue_users.append(user_info['username'])

        return jsonify({"queue": queue_users}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Endpoint to fetch a username by user ID
@app.route('/get-username/<user_id>', methods=['GET'])
def get_username(user_id):
    try:
        # Convert user_id to ObjectId if necessary
        if ObjectId.is_valid(user_id):
            user_id = ObjectId(user_id)
        else:
            return jsonify({"error": "Invalid user ID format"}), 400

        # Accessing the 'roles' collection
        collection = db['roles']

        # Find the user by user_id
        user = collection.find_one({"_id": user_id}, {"_id": 0, "username": 1})

        if user is None:
            return jsonify({"error": "User not found"}), 404

        return jsonify({"username": user['username']}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def check_user_status(tool_info, user_id):
    current_queue = tool_info.get('queue', [])
    waiting_queue = tool_info.get('waiting_queue', [])

    if user_id in current_queue:
        return {"message": f"User {user_id} is already in the queue", "queue_status": "In Queue"}
    elif user_id in waiting_queue:
        return {"message": f"User {user_id} is already in the waiting list", "queue_status": "In Waiting List"}

    return None

from flask import request, jsonify

@app.route('/add-to-queue', methods=['POST'])
def add_to_queue():
    try:
        # Extract data from the POST request
        data = request.json
        user_id = data.get('user_id')
        tool_id_str = data.get('tool_id')
        tool_id = ObjectId(tool_id_str)  # Convert string to ObjectId

        # Accessing the 'toolQueue' collection
        tool_queue_collection = db['toolQueue']
        tool_info = tool_queue_collection.find_one({"tool_id": tool_id})

        if tool_info is None:
            return jsonify({"error": "Tool not found"}), 404

        # Check if the user is already in any queue or waiting list
        user_status = check_user_status(tool_info, user_id)
        if user_status:
            # Get the current queue and waiting list
            current_queue = tool_info.get('queue', [])
            current_waiting_list = tool_info.get('waiting_queue', [])
            return jsonify({"user_status": user_status, "Queue": current_queue, "waiting": current_waiting_list}), 200

        # Get the queue limit for the specified tool
        queue_limit = tool_info.get('queue_limit', 0)

        # Check if the queue limit has been reached
        if len(tool_info.get('queue', [])) < queue_limit:
            # Add user to the queue for the specified tool
            tool_queue_collection.update_one(
                {"tool_id": tool_id},
                {"$push": {"queue": user_id}}
            )
            queue_status = "In Queue"
        else:
            # Add user to the waiting list for the specified tool
            tool_queue_collection.update_one(
                {"tool_id": tool_id},
                {"$push": {"waiting_queue": user_id}}
            )
            queue_status = "In Waiting List"

        # Retrieve service details from the 'tools' table
        tool_details = db['tools'].find_one({"_id": tool_id})
        if tool_details:
            namespace = tool_details.get('namespace')
            if namespace == "prom":
                pv_file_name = "prom_pv.yaml"
            else:
                pv_file_name = "bhub_pv.yaml"
            
            # Call the create_persistent_volume function to create the PersistentVolume
            result1 = create_persistent_volume(namespace, pv_file_name, user_id)
            print(result1)
            if "error" in result1:
                return jsonify({"error": result1["error"]}), 500

            # Get the current queue and waiting list
            current_queue = tool_info.get('queue', [])
            current_waiting_list = tool_info.get('waiting_queue', [])

            # Return success message along with service details, queue, and waiting list
            service_details = get_service_port(namespace, tool_details.get('service'))
            return jsonify({
                "message": f"User {user_id} added to {queue_status} for tool {tool_id_str}",
                "queue_status": queue_status,
                "service_details": service_details,
                "Queue": current_queue,
                "waiting": current_waiting_list
            }), 200
        else:
            return jsonify({"error": "Tool details not found"}), 404
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500



@app.route('/remove-from-queue', methods=['POST'])
def remove_from_queue():
    try:
        # Extract data from the POST request
        data = request.json
        user_id = data.get('user_id')
        tool_id_str = data.get('tool_id')
        tool_id = ObjectId(tool_id_str)  # Convert string to ObjectId

        # Accessing the 'toolQueue' collection
        tool_queue_collection = db['toolQueue']
        tool_info = tool_queue_collection.find_one({"tool_id": tool_id})

        if tool_info is None:
            return jsonify({"error": "Tool not found"}), 404

        # Get the current queue for the specified tool
        queue = tool_info.get('queue', [])

        # Check if the user is in the queue
        if user_id in queue:
            # Remove user from the queue for the specified tool
            tool_queue_collection.update_one(
                {"tool_id": tool_id},
                {"$pull": {"queue": user_id}}
            )
            return jsonify({"message": f"User {user_id} removed from queue for tool {tool_id_str}"}), 200
        else:
            return jsonify({"message": f"User {user_id} is not in the queue for tool {tool_id_str}"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def list_available_or_released_pvs():
    try:
        # Load Kubernetes configuration from default location
        config.load_kube_config()

        # Create a Kubernetes API client
        k8s = client.CoreV1Api()

        # Get all PersistentVolumes
        pvs = k8s.list_persistent_volume().items

        # List to store names of available or released PVs
        available_pvs = []

        # Iterate through each PersistentVolume and check if it's available or released
        for pv in pvs:
            # Check if PV status is available or released
            if pv.status.phase in ["Available", "Released"]:
                available_pvs.append(pv.metadata.name)

        return available_pvs

    except Exception as e:
        print("Error:", str(e))
        return []

from flask import jsonify

@app.route('/remove-user-from-tool-queues', methods=['DELETE'])
def remove_user_from_tool_queues_api():
    try:
        # Get the list of available or released persistent volumes
        available_pvs = list_available_or_released_pvs()
        
        removed_pvs = []

        # Iterate over each available PV
        for pv_name in available_pvs:
            # Extract user ID from the PV name
            pv_user_id = pv_name.split('-')[0]
            
            # Remove the user from the queue of tools associated with the PV
            for tool_id in db['toolQueue'].find():
               
                tool_pvs = tool_id.get('queue', [])
                # print(tool_pvs)
                
                if pv_user_id in tool_pvs:
                    removed_pvs.append(pv_name)
                    # Remove the user from the tool queue
                    db['toolQueue'].update_one(
                        {"_id": tool_id["_id"]},
                        {"$pull": {"queue": pv_user_id}}
                    )
        delete_all_pvs()
        return jsonify({"removed_pvs": removed_pvs}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route('/logout', methods=['POST'])
def logout():
    try:
        data = request.json
        user_id = data.get('user_id')

        if not user_id:
            return jsonify({"error": "user_id is required"}), 400

        # Remove user from all tool queues and waiting lists
        remove_user_from_all_queues(user_id)
        delete_all_pvs()
        return jsonify({"message": f"User {user_id} has been removed from all queues"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

def remove_user_from_all_queues(user_id):
    # Find all tools in the toolQueue collection
    tool_queue_collection = db['toolQueue']
    tools = tool_queue_collection.find()

    for tool in tools:
        tool_id = tool.get('tool_id')

        # Remove user from queue
        tool_queue_collection.update_one(
            {"tool_id": tool_id},
            {"$pull": {"queue": user_id}}
        )

        # Remove user from waiting list
        tool_queue_collection.update_one(
            {"tool_id": tool_id},
            {"$pull": {"waiting_queue": user_id}}
        )



@app.route('/check-and-move-user', methods=['POST'])
def check_and_move_user():
    try:
        # Extract data from the POST request
        data = request.json
        user_id = data.get('user_id')
        tool_id_str = data.get('tool_id')
        tool_id = ObjectId(tool_id_str)

        # Accessing the 'toolQueue' collection
        tool_queue_collection = db['toolQueue']

        # Check if the user is already in the queue
        tool_info = tool_queue_collection.find_one({"tool_id": tool_id})
        if tool_info is None:
            return jsonify({"error": "Tool not found"}), 404

        current_queue = tool_info.get('queue', [])
        current_waiting_list = tool_info.get('waiting_queue', [])
        queue_limit = tool_info.get('queue_limit', 0)

        if user_id in current_queue:
            return jsonify({"user_in_queue": True}), 200
        else:
            if len(current_queue) < queue_limit:
                if current_waiting_list:
                    # Move the top user from waiting list to queue
                    top_waiting_user = current_waiting_list[0]
                    tool_queue_collection.update_one(
                        {"tool_id": tool_id},
                        {"$push": {"queue": top_waiting_user}, "$pop": {"waiting_queue": -1}}
                    )
                    return jsonify({"user_in_queue": False, "user_moved_to_queue": top_waiting_user}), 200
                else:
                    return jsonify({"user_in_queue": False, "waiting_list_empty": True}), 200
            else:
                return jsonify({"user_in_queue": False, "queue_limit_reached": True}), 200

    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500

# Endpoint to delete the MariaDB tool by calling the delete_mariadb() function
@app.route('/uninstall-tool-mariadb', methods=['DELETE'])
def uninstall_tool_mariadb():
    try:
        # Call the delete_mariadb() function to delete the MariaDB tool
        result = delete_mariadb()
        if result[1] != 200:
            # Return error response if MariaDB deletion failed
            return result

        return jsonify({"message": "MariaDB tool uninstalled successfully."}), 200
    except Exception as e:
        return jsonify({"error": f"An error occurred: {e}"}), 500


@app.route('/uninstall-tool/<tool_id>', methods=['DELETE'])
def uninstall_tool(tool_id):
    try:
        # Accessing the 'tools' collection
        collection = db['tools']
        tool = collection.find_one({"_id": ObjectId(tool_id)})

        if tool is None:
            return jsonify({"error": "Tool not found"}), 404
        
        if tool.get("tool_name") == "MariaDB":
      # Call the delete_mariadb() function to delete the MariaDB tool
          result = delete_mariadb()
          if result[1] != 200:
              # Return error response if MariaDB deletion failed
              return result

          return jsonify({"message": "MariaDB tool uninstalled successfully."}), 200
        
        if tool.get("tool_name") == "Wordpress":
          # Call the delete_wordpress() function to delete the Wordpress tool
          result = delete_wordpress()
          if result[1] != 200:
              # Return error response if Wordpress deletion failed
              return result

          return jsonify({"message": "Wordpress tool uninstalled successfully."}), 200
        
        if tool.get("tool_name") == "Apache":
          # Call the delete_apache() function to delete the Apache tool
          result = delete_apache()
          if result[1] != 200:
              # Return error response if Apache deletion failed
              return result

          return jsonify({"message": "Apache tool uninstalled successfully."}), 200
        print("tool:", tool)

        if tool.get("tool_name") == "RabbitMQ":
          # Call the delete_rabbitmq() function to delete the RabbitMQ tool
          result = delete_rabbitmq()
          if result[1] != 200:
              # Return error response if RabbitMQ deletion failed
              return result

          return jsonify({"message": "RabbitMQ tool uninstalled successfully."}), 200
        
        if tool.get("tool_name") == "ArgoCD":
          # Call the delete_argocd() function to delete the ArgoCD tool
          result = delete_argocd()
          if result[1] != 200:
              # Return error response if ArgoCD deletion failed
              return result

          return jsonify({"message": "ArgoCD tool uninstalled successfully."}), 200
        
        if tool.get("tool_name") == "Jenkins":
          # Call the delete_jenkins() function to delete the Jenkins tool
          result = delete_jenkins()
          if result[1] != 200:
              # Return error response if Jenkins deletion failed
              return result

          return jsonify({"message": "Jenkins tool uninstalled successfully."}), 200

        if tool.get("tool_name") == "Zipkin":
          # Call the delete_zipkin() function to delete the Zipkin tool
          result = delete_zipkin()
          if result[1] != 200:
              # Return error response if Zipkin deletion failed
              return result

          return jsonify({"message": "Zipkin tool uninstalled successfully."}), 200

        helm_command = tool.get("helm_command")
        namespace = tool.get("namespace")

        print("helm_command:", helm_command)
        print("namespace:", namespace)
        # Check if helm_command is None
        if not helm_command:
          return jsonify({"error": "Helm command not found for the tool"}), 400
        # Extract pod name from helm_command
        pod_name = helm_command.split(" ")[4]
        
        # Create the helm uninstall command
        uninstall_command = f"helm uninstall {pod_name} -n {namespace}"

        # Execute the uninstall command
        command_result = execute_command(uninstall_command, tool['tool_name'])

        # Update the tool's installed status to "false" (as a string) in MongoDB
        update_result = collection.update_one({"_id": ObjectId(tool_id)}, {"$set": {"installed": "false"}})
        print("hi")

        return jsonify({"message": f"Tool {pod_name} uninstalled successfully", "command_output": command_result["output"]}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 200


if __name__ == "__main__":
    app.run(debug=True)