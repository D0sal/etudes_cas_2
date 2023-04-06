import json
from flask import Flask, jsonify
from find_image import main
# from your_file import your_function
app = Flask(__name__, static_folder='static')


@app.route('/')
def index():

    return app.send_static_file('index.html')

@app.route('/single/<text>', methods=['GET'])
def generate_single_image(text):
    data = {}
    data  = str(main(text))

    # return the images as a response
    return jsonify(images=data)

@app.route('/multiple/<text>', methods=['GET'])
def generate_multiple_images(text):
    data = {}
    data  = str(main(text))

    # return the images as a response
    return jsonify(images=data)

if __name__ == '__main__':
    app.run(debug=True)