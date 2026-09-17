from flask import Flask, jsonify
app = Flask(__name__)

@app.route("/")
def hello():
    return "<h1>ChaseLights v0.2 Test Server</h1><p>Server is running!</p><p><a href='/summary'>Go to Summary Page</a></p>"

@app.route("/test")
def test():
    return jsonify({"status": "ok", "version": "v0.2", "message": "ChaseLights test API working"})

if __name__ == "__main__":
    print("Starting ChaseLights v0.2 test server on http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, debug=False)