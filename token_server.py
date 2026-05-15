from flask import Flask
from flask import request
from flask_cors import CORS
import json

app = Flask(__name__)

CORS(app)


@app.route(
    "/token",
    methods=["POST"]
)
def guardar_token():

    data = request.json

    with open(
        "auth.json",
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            indent=4
        )

    print(
        "Auth actualizada."
    )

    return {
        "success": True
    }


app.run(
    host="0.0.0.0",
    port=5000
)