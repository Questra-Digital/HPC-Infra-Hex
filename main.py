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

        return {"message": f"Created PersistentVolume '{pv_name}' from '{file_name}' in namespace '{namespace}'"}
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
    try:
       
        pv_file_name = "bhub_pv.yaml"
        result = get_file_content(pv_file_name)

        # if result.status_code != 200:
            # return result

        valuefile = "values.yaml"
        result = get_file_content(valuefile)
        print(result)
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

        resultfinal =  execute_command(helm_command,tool_name)
        collection.update_one(
            {"tool_name": tool_name},
            {"$set": {"installed": "true"}}
        )

        return jsonify({"message": f"Started execution of Helm command for {tool_name} in the background."})
    
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

@app.route('/uninstall-tool/<tool_id>', methods=['DELETE'])
def uninstall_tool(tool_id):
    try:
        # Accessing the 'tools' collection
        collection = db['tools']
        tool = collection.find_one({"_id": ObjectId(tool_id)})

        if tool is None:
            return jsonify({"error": "Tool not found"}), 404

        helm_command = tool.get("helm_command")
        namespace = tool.get("namespace")

        # Extract pod name from helm_command
        pod_name = helm_command.split(" ")[4]
        
        # Create the helm uninstall command
        uninstall_command = f"helm uninstall {pod_name} -n {namespace}"

        # Execute the uninstall command
        command_result = execute_command(uninstall_command, tool['tool_name'])

        # Update the tool's installed status to "false" (as a string) in MongoDB
        update_result = collection.update_one({"_id": ObjectId(tool_id)}, {"$set": {"installed": "false"}})
        print("hi")

        return jsonify({"message": f"Tool {pod_name} uninstalled successfully", "command_output": command_result["output"]})
    except Exception as e:
        return jsonify({"error": str(e)}), 200


if __name__ == "__main__":
    app.run(debug=True)