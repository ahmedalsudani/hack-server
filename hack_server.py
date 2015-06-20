#! env python
from flask import Flask, Response, request
from flask.ext.redis import FlaskRedis
from flask.ext.cors import CORS, cross_origin
import json
import pickle
from os import environ

app = Flask(__name__)
cors = CORS(app)
app.config['REDIS_URL'] = environ['REDIS_URL']

data_store = FlaskRedis(app)

UNUSED_PROPERTIES = ['assignees', 'progress', 'owner']
DROPPED_PROPERTIES = ['assignees']

def jsonResponse(data):
    return Response(headers={'Access-Control-Allow-Origin': '*'}, content_type='application/json', response=json.dumps(data))

@app.route('/cards/', methods=['GET'])
def getAllCards():
    print("get all")
    objects = [pickle.loads(data_store.get(key)) for key in data_store.keys()]
    return jsonResponse(objects)

@app.route('/cards/<string:id>', methods=['GET'])
def getCard(id):
    print("get {0}".format(id))
    object = data_store.get(id)
    if object is None:
        return Response(response=json.dumps('Not found'), status=404)
    else:
        unpickled = pickle.loads(object)
        try:
            unpickled['id']
        except:
            unpickled['id'] = id
        return jsonResponse(json.dumps(unpickled))

@app.route('/cards/<string:id>', methods=['POST'])
def setCard(id):
    print("set {0}".format(id))
    object = json.loads(request.data)
    for prop in UNUSED_PROPERTIES:
        object[prop] = None
    for prop in DROPPED_PROPERTIES:
        del object[prop]
    redis_response = data_store.set(id, pickle.dumps(object))
    if redis_response:
        # unpickled = pickle.loads(data_store.get(id))
        # return jsonResponse(unpickled)
        return getCard(id)

@app.route('/cards/<string:id>', methods=['DELETE'])
def deleteCard(id):
    response = data_store.delete(id)
    return jsonResponse('Deleted {0} objects'.format(response))

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000)
