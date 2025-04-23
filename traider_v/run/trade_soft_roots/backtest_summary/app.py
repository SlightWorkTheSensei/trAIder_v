from flask import Flask, request, render_template, send_from_directory, jsonify
import os
from modules.fetch_data import fetch_data_handler
from modules.performance import get_performance
from modules.visualization import create_charts

app = Flask(__name__)
DATA_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')

@app.route('/')
def index():
    files = os.listdir(DATA_FOLDER)
    return render_template('index.html', files=files)

@app.route('/fetch', methods=['POST'])
def fetch_data():
    return fetch_data_handler(request, DATA_FOLDER)

@app.route('/data/<filename>')
def data(filename):
    return send_from_directory(DATA_FOLDER, filename)

@app.route('/performance/<int:index>', methods=['GET'])
def performance(index):
    return get_performance(request, index)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1253)
