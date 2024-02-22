from flask import Flask, request, Response, jsonify
from pymongo import MongoClient
from bson import Binary, ObjectId
from bson.errors import InvalidId


app = Flask(__name__)
client = MongoClient('mongodb://localhost:27017/')
db = client['photo_upload_db']
collection = db['images']


@app.route('/upload', methods=['POST'])
def upload_file():
    uploaded_file = request.files.get('file')
    if not uploaded_file:
        return jsonify({'message': 'No file provided'}), 400

    if not allowed_file(uploaded_file.filename):
        return jsonify({'message': 'Invalid file format'}), 400

    try:
        image_data = Binary(uploaded_file.read())
        document_id = collection.insert_one({'image': image_data}).inserted_id
        return jsonify({'message': 'Image uploaded successfully', 'id': str(document_id)})
    except Exception as e:
        return jsonify({'message': f'An error occurred while uploading the image: {str(e)}'}), 500


@app.route('/image/<image_id>', methods=['GET'])
def get_image(image_id):
    try:
        document = collection.find_one({'_id': ObjectId(image_id)})
        if document:
            return Response(document['image'], mimetype='image/jpeg')
        else:
            return jsonify({'message': 'Image not found'}), 404
    except InvalidId:
        return jsonify({'message': 'Invalid image ID'}), 400


@app.route('/delete/<image_id>', methods=['DELETE'])
def delete_image(image_id):
    try:
        result = collection.delete_one({'_id': ObjectId(image_id)})
        if result.deleted_count > 0:
            return jsonify({'message': 'Image deleted successfully'})
        else:
            return jsonify({'message': 'Image not found'}), 404
    except InvalidId:
        return jsonify({'message': 'Invalid image ID'}), 400


def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


if __name__ == '__main__':
    app.run(debug=True)
