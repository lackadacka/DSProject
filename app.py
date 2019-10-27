from flask import Flask
import requests
import random

from FileTree import FileTree

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/init')
def init():
    global file_tree
    file_tree = FileTree()
    result = 0

    for datanode in datanodes:
        response = requests.get(datanode + "/init").json()
        result += response['size']
    return {'size': result}


@app.route('/create')
def create():
    file_path = requests.args.get('filePath', type=str)
    replication_list = []
    while len(replication_list) < 3 and len(datanodes) >= 3:
        datanode = random.choice(datanodes)
        if not replication_list.__contains__(datanode):
            replication_list.append(datanode)
    file_tree.add_node(file_path, False, replication_list)
    return {'nodes': replication_list}

@app.route('/read')
def read():
    file_path = requests.args.get('filePath', type=str)
    return file_tree.search_node(file_path)







if __name__ == '__main__':
    file_tree = FileTree()
    app.run()
    datanodes = []
