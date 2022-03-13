from flask import Flask, request, jsonify
from lib.migration import StateFile

app = Flask(__name__)


@app.get('/migrations')
def get_migrations():
    def cut(name): return name.replace('.json', '', 1)
    list_files = list(map(cut, StateFile.list_files()))
    return jsonify(list_files)


@app.post('/migrations')
def add_migration():
    if request.is_json:
        return StateFile.new(request.get_json()), 201
    return {"error": "Request must be JSON"}, 415


@app.delete('/migrations')
def del_migration():
    if request.is_json:
        data = request.get_json()
        return StateFile.remove(data['remove']), 200
    return {"error": "Request must be JSON"}, 415
