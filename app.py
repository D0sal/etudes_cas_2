from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def index():

    return app.send_static_file('index.html')

@app.route('/single/<text>', methods=['GET'])
def generate_single_image(text):
    image = text

    # return the image as a response
    return jsonify(image=image)

@app.route('/multiple/<text>', methods=['GET'])
def generate_multiple_images(text):
    images = text

    # return the image as a response
    return jsonify(images=images)

if __name__ == '__main__':
    app.run(debug=True)