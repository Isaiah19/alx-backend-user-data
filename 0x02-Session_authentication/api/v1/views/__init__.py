from flask import Blueprint, jsonify

app_views = Blueprint('app_views', __name__)

# Example view
@app_views.route('/status', methods=['GET'])
def status():
    return jsonify({"status": "OK"})

