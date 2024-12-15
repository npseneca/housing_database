import pymongo

from flask import Flask
from flask import request, jsonify
from flask import send_from_directory
from flask_cors import CORS

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

@app.route("/search", methods = ["Post", "GET"])
def Search():
    try: 
        query = {"zipcode": "20131"}
        
        results = mycul.find(query, {"_id": 0, "detail_url": 1}).limit(5)
        
        listings = list(results)
        
        return jsonify(listings), 200
    except Exception as e:
        return f"Error: {e}"
    
    

if __name__ == "__main__":
    app.run()
