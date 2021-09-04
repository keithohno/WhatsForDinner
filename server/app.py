from os import write
from flask import Flask, jsonify, request, session
from flask_cors import CORS, cross_origin
import pymongo
import os
import json
import uuid

app = Flask(__name__)
app.config.update(SECRET_KEY=os.urandom(16))
app.config.from_object(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})


# setup MongoDB
def setup_db():
    uri = "mongodb+srv://cluster0.a55mv.mongodb.net/data?authSource=%24external&authMechanism=MONGODB-X509&retryWrites=true&w=majority"
    client = pymongo.MongoClient(
        uri, tls=True, tlsCertificateKeyFile="../mongocert.pem"
    )
    db = client["recipes"]
    return db["valid"]


db = setup_db()


# query route
@app.route("/query", methods=["POST"])
@cross_origin(supports_credentials=True)
def query():
    # create new session if we need one
    if not 'sid' in session:
        session['sid'] = uuid.uuid4()
        session['cpos'] = 0
    print(session['sid'])
    # extract query from POST
    post_data = request.get_json()
    query = post_data["query"]
    session['query'] = query
    # get MongoDB query results (list of ten)
    res = list(db.find(query)[session['cpos']:session['cpos']+10])
    for r in res:
        r["_id"] = str(r["_id"])
    response_object = {"res": res}
    # response
    return jsonify(response_object)


# query route
@app.route("/querynext", methods=["GET"])
@cross_origin(supports_credentials=True)
def querynext():
    # retrieve query and curosr position
    query = session['query']
    session['cpos'] += 10
    # return results of find sliced 10 positions ahead
    res = list(db.find(query)[session['cpos']:session['cpos']+10])
    for r in res:
        r["_id"] = str(r["_id"])
    response_object = {"res": res}
    # response
    return jsonify(response_object)


if __name__ == "__main__":
    app.run()
