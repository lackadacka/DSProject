from flask import Flask
import requests
import random
from apscheduler.schedulers.background import BackgroundScheduler
from FileTree import FileTree
import datetime
app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'


def find_datanodes():
    subnet = '10.91.51.'
    for i in range(256):
        print(i)
        ip = subnet + str(i) + ":5000"
        try:
            response = requests.get("http://" + ip + "/health")
        except requests.exceptions.RequestException:
            continue

        datanodes.append(ip)
        print(ip + " success")



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
    # replication_list = []
    # while len(replication_list) < 3 and len(datanodes) >= 3:
    #     datanode = random.choice(datanodes)
    #     if not replication_list.__contains__(datanode):
    #         replication_list.append(datanode)
    # file_tree.add_node(file_path, False, replication_list)
    # return {'nodes': replication_list}

    datanode = random.choice(datanodes)
    file_tree.add_node(file_path, False, list(datanode))
    return {'node': datanode}

@app.route('/read')
def read():
    file_path = requests.args.get('filePath', type=str)
    return file_tree.search_node(file_path)


@app.route('/write')
def write():
    file_path = requests.args.get('filePath', type=str)
    datanode = random.choice(datanodes)
    file_tree.add_node(file_path, False, list(datanode))
    return {'node': datanode}


@app.route('/delete')
def delete():
    file_path = requests.args.get('filePath', type=str)
    return file_tree.delete_node(file_path)


@app.route('/info')
def info():
    file_path = requests.args.get('filePath', type=str)
    return file_tree.info_node(file_path)


@app.route('/copy')
def copy():
    file_path = requests.args.get('filePath', type=str)
    node = file_tree.search_node(file_path)[0]
    return request_copy(file_path, node)

def request_copy(file_path, node):
    return 200


@app.route('/replicate')
def replicate():
    file_path = requests.args.get('filePath', type=str)
    occupied = file_tree.search_node(file_path)
    for dn in datanodes:
        if dn not in occupied:
            return dn


if __name__ == '__main__':

    file_tree = FileTree()
    datanodes = []
    scheduler = BackgroundScheduler()
    job = scheduler.add_job(find_datanodes, 'interval', seconds=30)
    scheduler.start()
    app.run(debug=True, use_reloader=False)

