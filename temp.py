from flask import Flask, request, jsonify
from kubernetes import client, config
from kubernetes.stream import stream
import websocket
import ssl

app = Flask(__name__)

def execute_command_in_pod(namespace, pod_name, commands):
    try:
        # Load Kubernetes configuration
        config.load_kube_config()

        # Create an instance of the Kubernetes API client
        api_instance = client.CoreV1Api()

        # Construct the command payload
        exec_command = [
            "/bin/bash",
            "-c",
            "; ".join(commands)  # Join multiple commands with ;
        ]

        # Construct the WebSocket URL
        ws_url = f"wss://192.168.56.10:6443/api/v1/namespaces/{namespace}/pods/{pod_name}/exec?command={','.join(exec_command)}&stdin=true&stdout=true&stderr=true&tty=true"

        # Create a WebSocket connection
        ws = websocket.create_connection(ws_url, sslopt={"cert_reqs": ssl.CERT_NONE})
        
        # Send a ping every 60 seconds to keep the connection alive
        def ping_websocket():
            while True:
                ws.ping()
                time.sleep(60)

        ping_thread = Thread(target=ping_websocket)
        ping_thread.daemon = True
        ping_thread.start()

        # Read the output from the WebSocket
        output = ""
        while True:
            message = ws.recv()
            if not message:
                break
            output += message

        print("Command executed successfully. Output:")
        print(output)
        return output

    except Exception as e:
        print(f"Error executing command in pod: {e}")
        return ""

@app.route('/execute-command', methods=['POST'])
def execute_command():
    try:
        data = request.json
        namespace = data.get('namespace')
        pod_name = data.get('pod_name')
        commands = data.get('commands')

        if not namespace or not pod_name or not commands:
            return jsonify({"error": "Missing required parameters"}), 400

        result = execute_command_in_pod(namespace, pod_name, commands)
        return jsonify({"result": result}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
