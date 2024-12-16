import pymongo

from flask import Flask
from flask import request, jsonify
from flask import send_from_directory
from flask_cors import CORS

import os

from openai import OpenAI

with open('secrets.env') as f:
    secrets = f.readlines()


for secret in secrets:
    name, password = secret.split('=')
    name, password = name.strip(), password.strip()
    os.environ[name] = password


# intialize OpenAI client

openAiClient = OpenAI(
    api_key = os.environ.get("openaiKey"),
    organization = os.environ.get("orgId")
)

#replace with the right url, database, and collection
myclient = pymongo.MongoClient("mongodb+srv://npseneca:xnPc5jSVrOoaur0t@cs452.gtgjg.mongodb.net/?retryWrites=true&w=majority&appName=cs452")
mydb = myclient['testDB']
mycul = mydb['test']

app = Flask(__name__)
cors = CORS(app)
app.config["CORS_HEADERS"] = "Content-Type"

@app.route("/")
def home():
    return send_from_directory(".", "index.html")

@app.route("/list", methods = ["Post", "GET"])
def Push():
    content = request.get_json()
    mycul.insert_one(content)
    return "Push initiated"

#TODO: implement search function which uses ChatGPT
@app.route("/search", methods = ["Post", "GET"])
def Search():
    try: 
        with open('log.txt', 'a') as f:
            print(request, file=f)
        q = request.args.get('q')

        

        query = {"zipcode": 20131}
        
        results = mycul.find(query, {"_id": 0, "detail_url": 1}).limit(5)
        
        listings = list(results)
        
        return jsonify(listings), 200
    except Exception as e:
        return f"Error: {e}"
    
# OpenAI helper functions
def getChatGptResponse(content):
    instructions = commonSqlOnlyRequest = "Give me a MongoDB select statement that answers the question. Only respond with MongoDB syntax. If there is an error do not expalin it!"
    stream = openAiClient.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": content}],
        stream=True,
    )

    responseList = []
    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            responseList.append(chunk.choices[0].delta.content)

    result = "".join(responseList)
    return result

if __name__ == "__main__":
    app.run()
