from os import write
from flask import Flask, jsonify, request
from flask_cors import CORS
import pymongo
import json

# app setup with CORS
app = Flask(__name__)
app.config.from_object(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})


# setup MongoDB
def setup_db():
    uri = "mongodb+srv://cluster0.a55mv.mongodb.net/data?authSource=%24external&authMechanism=MONGODB-X509&retryWrites=true&w=majority"
    client = pymongo.MongoClient(
        uri, tls=True, tlsCertificateKeyFile="../X509-cert-192195340096089653.pem"
    )
    db = client["recipes"]
    return db["valid"]


db = setup_db()


# query route
@app.route("/query", methods=["POST"])
def query():
    post_data = request.get_json()
    query = post_data["query"]
    print("query received: " + json.dumps(query, indent=4))
    res = db.find_one(query)
    res["_id"] = str(res["_id"])
    response_object = {"res": res}
    print("responded with: " + json.dumps(res, indent=4))
    return jsonify(response_object)


if __name__ == "__main__":
    app.run()
