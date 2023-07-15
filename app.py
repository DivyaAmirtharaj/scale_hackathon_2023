from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/kaboom', methods=['POST'])
def post_data():
    # Get JSON data from the request
    channel_id = request.form.get('channel_id')
    text = request.form.get('text')
    user_id = request.form.get('user_id')

    data = "\n".join([channel_id, text, user_id])

    # Do something with the data here

    # Send a response
    return jsonify({"status": "success", "data": data}), 200