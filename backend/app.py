from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def hello_world():
    return 'Hello, World! This is a simple Flask server.'

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
