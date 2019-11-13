from flask import Flask, request, send_from_directory, redirect, Response
import os
import requests


app = Flask(__name__)
file_names = {}
files = []
free_index = 0
namenode = ""


def create_dir(path):
    paths = path.split('/')
    current_path = ''
    for p in paths[:-1]:
        current_path += '/' + p
        if not os.path.exists(current_path):
            os.mkdir(current_path)


@app.route('/download')
def download_file():
    path = request.args.get('File-Name', type=str)
    file_id = request.args.get('File-Id', type=int)
    chunk_id = request.args.get('Chunk-Id', type=int)
    chunk_length = request.args.get('Chunk-Length', type=str)
    if file_names.get(file_id) != path.split('/')[-1]:
        file_names.update({file_id, (len(files), path.split('/')[-1])})
    files[file_names.get(file_id)] += request.data
    replications = request.headers.get('repl_number', type=int)
    if replications:
        replications += 1
    else:
        replications = 1
    if replications < 3:
        r = requests.get(url=namenode, params={'path': path})
        address = r.json().get('address')
        if address:
            request.args.add('replications', replications + 1)
            redirect(address)

    if chunk_id == chunk_length:
        create_dir(path)
        with open(os.path.join(path.split('/')[:-1], path.split('/')[-1]), "wb") as fp:
            fp.write(files[file_names.get(file_id)[0]])
        curr_index = file_names.get(file_id)[0]
        del files[curr_index]
        del file_names[file_id]
        for d in file_names:
            if d[0] > curr_index:
                file_names.update({d[0], (d[1][0] - 1, d[1][1])})

    return Response(status=200)



@app.route('/create')
def create_file():
    path = request.args.get('path', type=str)
    create_dir(path)
    replications = request.headers.get('repl_number', type=int)
    if replications:
        if replications < 3:
            r = requests.get(url=namenode, params={'path': path})
            address = r.json()
            request.args.add('replications', replications + 1)
            redirect(address)
    open(path, 'a').close()
    return Response(status=200)



@app.route('/upload')
def upload_file():
    path = request.args.get('path', type=str)
    try:
        return send_from_directory(path, attachment_filename=path[:-1])
    except Exception as e:
        return str(e)


@app.route('/health')
def health():
    global namenode
    namenode = request.remote_addr
    return Response(status=200)


@app.route('/delete')
def delete():
    path = request.args.get('path')
    os.remove(path)
    return Response(status=200)



@app.route('/rmdir')
def rmdir():
    path = request.args.get('path')
    os.system("rm -rf " + path)
    return Response(status=200)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
