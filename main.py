import vagrant

from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import yaml
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

v = vagrant.Vagrant()

# mongo_uri = "mongodb+srv://gamerobuddy:SKdBdjWiu3E5rKxC@cluster0.3exxg5m.mongodb.net/?retryWrites=true&w=majority"

# # Create a MongoDB client
# client = MongoClient(mongo_uri)

# db = client['Cluster0']

# if client.server_info():  # Check if the client is connected
#     print("Connected to MongoDB")

def ensure_all_machines_running():
    """Ensures that all Vagrant machines are running."""
    # Start all machines if they are not running
    v.up()


def generate_vagrantfile(payload):
    # Extract information from the payload
    nums_vms = payload["nums_vms"]-1
    vm_box = payload["vm_box"]
    first_ip = payload["boxes"][0]["ip"]
    master_node_name = payload["boxes"][0]["name"]
    vm_memory = payload.get("vm_memory", 2048)  # Default to 2048 if not specified in payload
    vm_cpu = payload.get("vm_Cpu", 2)  # Default to 2 CPUs if not specified in payload

    # Get the first three octets of the IP address
    first_three_octets = '.'.join(first_ip.split('.')[:3])

    # Vagrantfile content template
    vagrantfile_content = f"""IMAGE_NAME = "{vm_box}"
N = {nums_vms}

Vagrant.configure("2") do |config|
    config.ssh.insert_key = false

    config.vm.provider "virtualbox" do |v|
        v.memory = {vm_memory}
        v.cpus = {vm_cpu}
    end
      
    config.vm.define "{master_node_name}" do |master|
        master.vm.box = IMAGE_NAME
        master.vm.network "private_network", ip: "{first_ip}"
        master.vm.hostname = "{master_node_name}"
        master.vm.provision "ansible" do |ansible|
            ansible.playbook = "kubernetes-setup/master-playbook.yml"
        end
    end

    (1..N).each do |i|
        config.vm.define "node-#{{i}}" do |node|
            node.vm.box = IMAGE_NAME
            node.vm.network "private_network", ip: "{first_three_octets}.{{i + 10}}"
            node.vm.hostname = "node-#{{i}}"
            node.vm.provision "ansible" do |ansible|
                ansible.playbook = "kubernetes-setup/node-playbook.yml"
            end
        end
    end
end
"""

    # Write the Vagrantfile content to a file
    with open("Vagrantfile", "w") as file:
        file.write(vagrantfile_content)

    print("\nVagrantfile generated successfully!")

# Example usage with the provided payload


 

@app.route('/vagrant_status', methods=['GET'])
def vagrant_status():
    try:
        # Get the status of all virtual machines
        status = v.status()

        return jsonify({'result': 'success', 'status': status})

    except Exception as e:
        return jsonify({'result': 'error', 'message': str(e)}), 500

import subprocess

@app.route('/vagrant_up_all', methods=['GET'])
def vagrant_up_all():
    try:
        # Start the Vagrant machines in a separate process
        subprocess.Popen(['vagrant', 'up'])

        return jsonify({'result': 'success', 'message': 'Vagrant up command initiated'})

    except Exception as e:
        return jsonify({'result': 'error', 'message': str(e)}), 500

@app.route('/run-command/<machine_name>', methods=['POST'])
def run_command(machine_name):
    print("kkk")
    # try:
    #     # Ensure the specific virtual machine is running
    #     # v.ssh is assumed to be a function or class that handles SSH connections

    #     # Extract the command from the POST request body
    #     command = request.json.get('command')

    #     if not command:
    #         return jsonify({'result': 'error', 'message': 'Command not provided in the request body'}), 400

    #     result = v.ssh(command=command, vm_name=machine_name)

    #     # Return a JSON response with the result and output
    #     return jsonify({'result': 'success', 'output': result})

    # except Exception as e:
    #     # In case of an exception, return an error response with the exception message
    return jsonify({'result': 'error', 'message': str("master")}), 500

@app.route('/generate_vagrantfile', methods=['POST'])
def generate_vagrantfile_api():
    data = request.get_json()
    generate_vagrantfile(data)
    return jsonify({"message": "Vagrantfile generated successfully!"})

# def run_ansible_playbook():
#     try:
#         # Use the 'ansible' provisioner to run the playbook

#         subprocess.run(['vagrant', 'provision', '--provision-with', 'ansible'], check=True)

#         return "Ansible playbook executed successfully on the VMs."

#     except subprocess.CalledProcessError as e:
#         return f"Error running Ansible playbook: {str(e)}"

#     except Exception as e:
#         return f"An error occurred: {str(e)}"

# @app.route('/install-playbook/<int:script_id>', methods=['GET'])
# def install_playbook_on_vms(script_id):
#     try:
#         script_document = yml_collection.find_one({"script_id": script_id})
#         if script_document:
#             yaml_data = script_document["script_data"]
            
#             # Define the path to the playbook/main.yml file
#             playbook_file_path = os.path.join(os.path.dirname(__file__), 'playbook', 'main.yml')
            
#             # Write the YAML data to playbook/main.yml
#             with open(playbook_file_path, 'w') as playbook_file:
#                 yaml.dump(yaml_data, playbook_file)
#             # Run the Ansible playbook
#             result = run_ansible_playbook()
#             return jsonify({'result': 'success', 'message': result})
#         else:
#             return jsonify({'result': 'error', 'message': 'Script not found'}), 404
    
#     except Exception as e:
#         return jsonify({'result': 'error', 'message': str(e)}), 500
    
# yml_collection = db["playbook_scripts"]

# @app.route("/upload-playbook", methods=["POST"])
# def upload_yaml():
#     try:
#         uploaded_file = request.files["file"]
#         if not uploaded_file:
#             return jsonify({"error": "No file uploaded"}), 400

#         script_id = int(request.form.get("script_id", 0))
#         if script_id <= 0:
#             return jsonify({"error": "Invalid script_id"}), 400

#         tool_name = request.form.get("tool_name", "")

#         if not tool_name:
#             return jsonify({"error": "Tool name is required"}), 400

#         yaml_data = yaml.safe_load(uploaded_file.read())
#         if not yaml_data:
#             return jsonify({"error": "Invalid YAML file"}), 400

#         yml_collection.insert_one({
#             "script_id": script_id,
#             "script_data": yaml_data,
#             "tool_name": tool_name
#         })
        
#         return jsonify({"message": "YAML file uploaded successfully"}), 200

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# @app.route("/get-playbook/<int:script_id>", methods=["GET"])
# def get_yaml_script(script_id):
    script_document = yml_collection.find_one({"script_id": script_id})
    if script_document:
        return jsonify(script_document["script_data"]), 200
    else:
        return jsonify({"error": "Script not found"}), 404
    
if __name__ == '__main__':
    app.run(debug=True)