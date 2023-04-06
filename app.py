import os
from flask import Flask, jsonify
# from your_file import your_function
app = Flask(__name__)

@app.route('/')
def index():

    return app.send_static_file('index.html')

@app.route('/single/<text>', methods=['GET'])
def generate_single_image(text):
    # image_paths = python_script(text)
    # closest_image = image_paths[0]

    # return the image as a response
    return jsonify(image=text)

@app.route('/multiple/<text>', methods=['GET'])
def generate_multiple_images(text):
    images = text

    # return the images as a response
    return jsonify(images=text)

if __name__ == '__main__':
    app.run(debug=True)