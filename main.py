import vagrant

from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import yaml
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

v = vagrant.Vagrant()

mongo_uri = "mongodb+srv://gamerobuddy:SKdBdjWiu3E5rKxC@cluster0.3exxg5m.mongodb.net/?retryWrites=true&w=majority"

# Create a MongoDB client
client = MongoClient(mongo_uri)

db = client['Cluster0']

if client.server_info():  # Check if the client is connected
    print("Connected to MongoDB")

def ensure_all_machines_running():
    """Ensures that all Vagrant machines are running."""
    # Start all machines if they are not running
    v.up()


def generate_vagrantfile(payload):
    vagrantfile_content = f"""# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.require_version ">= 2.3.0"

VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.box = "{payload['vm_box']}"
  config.vm.box_version = "{payload['vm_box_version']}"
  config.ssh.insert_key = false
  config.vm.provider "virtualbox"

  config.vm.provider :virtualbox do |v|
    v.memory = {payload['vm_memory']}
    v.cpus = {payload['vm_Cpu']}
    v.linked_clone = true
  end

  boxes = [
"""

    for vm in payload['boxes']:
        vagrantfile_content += f"""    {{ :name => "{vm['name']}", :ip => "{vm['ip']}" }},
"""

    vagrantfile_content += f"""  ]
  
  # Define VMs with dynamic private IP addresses.
  boxes.each do |opts|
    config.vm.define opts[:name] do |config|
      config.vm.hostname = opts[:name] + ".k8s.test"
      config.vm.network :private_network, ip: opts[:ip]

      # Provision all the VMs using Ansible after the last VM is up.
      if opts[:name] == "{payload['boxes'][-1]['name']}"
        config.vm.provision "ansible" do |ansible|
          ansible.playbook = "playbook/main.yml"
          ansible.inventory_path = "playbook/inventory"
          ansible.config_file = "playbook/ansible.cfg"
          ansible.limit = "all"
        end
      end
    end
  end
end
"""

    with open("Vagrantfile", "w") as file:
        file.write(vagrantfile_content)

    print("\nVagrantfile generated successfully!")



    with open("playbook/inventory", "w") as inventory_file:
        inventory_file.write(f"[k8s-master]\nmaster ansible_host={payload['boxes'][0]['ip']}\n\n")
        
        inventory_file.write("[k8s-nodes]\n")
        for vm in payload['boxes'][1:]:
            inventory_file.write(f"{vm['name']} ansible_host={vm['ip']}\n")
        inventory_file.write("\n")

        inventory_file.write("[k8s:children]\n")
        inventory_file.write("k8s-master\nk8s-nodes\n\n")

        inventory_file.write("[k8s:vars]\n")
        inventory_file.write("ansible_user=vagrant\n")
        inventory_file.write("ansible_ssh_private_key_file=~/.vagrant.d/insecure_private_key\n")

    print("Ansible inventory file generated successfully!")
 

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
    try:
        # Ensure the specific virtual machine is running
        # v.ssh is assumed to be a function or class that handles SSH connections

        # Extract the command from the POST request body
        command = request.json.get('command')

        if not command:
            return jsonify({'result': 'error', 'message': 'Command not provided in the request body'}), 400

        result = v.ssh(command=command, vm_name=machine_name)

        # Return a JSON response with the result and output
        return jsonify({'result': 'success', 'output': result})
 
    except Exception as e:
        # In case of an exception, return an error response with the exception message
        return jsonify({'result': 'error', 'message': str(e)}), 200

@app.route('/generate_vagrantfile', methods=['POST'])
def generate_vagrantfile_api():
    data = request.get_json()
    generate_vagrantfile(data)
    playbook_file_path = os.path.join(os.path.dirname(__file__), 'playbook', 'main.yml')
    echo_document = yml_collection.find_one({"tool_name": "echo"})
    echo_data = echo_document["script_data"]

    # Write the YAML data to playbook/main.yml
    with open(playbook_file_path, 'w') as playbook_file:
        yaml.dump(echo_data, playbook_file)
    return jsonify({"message": "Vagrantfile generated successfully!"})

def run_ansible_playbook():
    try:
        # Use the 'ansible' provisioner to run the playbook

        subprocess.run(['vagrant', 'provision', '--provision-with', 'ansible'], check=True)

        return "Ansible playbook executed successfully on the VMs."

    except subprocess.CalledProcessError as e:
        return f"Error running Ansible playbook: {str(e)}"

    except Exception as e:
        return f"An error occurred: {str(e)}"

@app.route('/install-playbook/<string:tool_name>', methods=['GET'])
def install_playbook_on_vms(tool_name):
    try:
        script_document = yml_collection.find_one({"tool_name": tool_name})
        if script_document:
            yaml_data = script_document["script_data"]
            
            # Define the path to the playbook/main.yml file
            playbook_file_path = os.path.join(os.path.dirname(__file__), 'playbook', 'main.yml')
            
            # Write the YAML data to playbook/main.yml
            with open(playbook_file_path, 'w') as playbook_file:
                yaml.dump(yaml_data, playbook_file)

            yml_collection.update_one({"tool_name": tool_name}, {"$set": {"is_installed": True}})
            result = run_ansible_playbook()
            # Continue with the execution of your Python code
            os.remove(playbook_file_path)
            echo_document = yml_collection.find_one({"tool_name": "echo"})
            echo_data = echo_document["script_data"]

            # Write the YAML data to playbook/main.yml
            with open(playbook_file_path, 'w') as playbook_file:
                yaml.dump(echo_data, playbook_file)
            
            return jsonify({'result': 'success', 'message': result})
        else:
            return jsonify({'result': 'error', 'message': 'Script not found'}), 404
    
    except Exception as e:
        return jsonify({'result': 'error', 'message': str(e)}), 500
    
yml_collection = db["playbook_scripts"]

@app.route("/upload-playbook", methods=["POST"])
def upload_yaml():
    try:
        uploaded_file = request.files["file"]
        if not uploaded_file:
            return jsonify({"error": "No file uploaded"}), 400

        script_id = int(request.form.get("script_id", 0))
        if script_id <= 0:
            return jsonify({"error": "Invalid script_id"}), 400

        tool_name = request.form.get("tool_name", "")

        if not tool_name:
            return jsonify({"error": "Tool name is required"}), 400

        yaml_data = yaml.safe_load(uploaded_file.read())
        if not yaml_data:
            return jsonify({"error": "Invalid YAML file"}), 400

        yml_collection.insert_one({
            "script_id": script_id,
            "script_data": yaml_data,
            "tool_name": tool_name,
            "is_installed": False
        })
        
        return jsonify({"message": "YAML file uploaded successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/get-playbook/<int:script_id>", methods=["GET"])
def get_yaml_script(script_id):
    script_document = yml_collection.find_one({"script_id": script_id})
    if script_document:
        return jsonify(script_document["script_data"]), 200
    else:
        return jsonify({"error": "Script not found"}), 404

@app.route('/get-all-playbooks', methods=['GET'])
def get_all_playbooks():
    try:
        # Retrieve all documents from the collection
        all_playbooks = list(yml_collection.find({}))
        
        # Create a list to store the results
        playbooks_list = []
        
        # Iterate through the documents and extract relevant information
        for playbook in all_playbooks:
            playbook_info = {
                "script_id": playbook["script_id"],
                "tool_name": playbook["tool_name"],
                "is_installed": playbook["is_installed"]
            }
            playbooks_list.append(playbook_info)
        
        return jsonify({'result': 'success', 'playbooks': playbooks_list})
    
    except Exception as e:
        return jsonify({'result': 'error', 'message': str(e)}), 500
    
if __name__ == '__main__':
    app.run(debug=True)