from flask import Flask, jsonify
import threading
from kubernetes import client, config
from kubernetes.stream import stream

app = Flask(__name__)

# Global variable to store the command output
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
def execute_command():
    name = "pythonserver-chart-7fcbccf94-tq5kn"
    namespace = "default"
    command = "helm upgrade --cleanup-on-fail --install my-jupyter jupyterhub/jupyterhub --namespace jhub --create-namespace --values values.yaml"

    # Execute the pod_exec function in a background thread
    thread = threading.Thread(target=pod_exec, args=(name, namespace, command))
    thread.start()

    return jsonify({"message": "Command execution started."})

@app.route('/get-status')
def get_status():
    global output
    return jsonify({"status": output})

if __name__ == '__main__':
    app.run(debug=True)
