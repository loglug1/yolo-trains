from flask import Flask, send_from_directory

app = Flask(__name__)


# Serves content from the static directory to the root URL
@app.route("/")
@app.route("/<path:file>")
def static_page(file = "index.html"):
    return send_from_directory("static", file)

