"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Post, Comment, Media, Follower

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints

@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([user.serialize() for user in users]), 200

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get(user_id)
    if user:
        return jsonify(user.serialize()), 200
    return jsonify({'message': 'Usuario no encontrado'}), 404

@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    new_user = User(
        username=data['username'],
        firstname=data.get('firstname'),
        lastname=data.get('lastname'),
        email=data['email'],
        password=data['password'],
        is_active=data.get('is_active', True)
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify(new_user.serialize()), 201

@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'Usuario no encontrado'}), 404

    data = request.get_json()
    user.username = data.get('username', user.username)
    user.firstname = data.get('firstname', user.firstname)
    user.lastname = data.get('lastname', user.lastname)
    user.email = data.get('email', user.email)
    user.password = data.get('password', user.password)
    user.is_active = data.get('is_active', user.is_active)

    db.session.commit()
    return jsonify(user.serialize()), 200

@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'Usuario no encontrado'}), 404

    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'Usuario eliminado'}), 200

@app.route('/posts', methods=['GET'])
def get_posts():
    posts = Post.query.all()
    return jsonify([post.serialize() for post in posts]), 200

@app.route('/posts/<int:post_id>', methods=['GET'])
def get_post(post_id):
    post = Post.query.get(post_id)
    if post:
        return jsonify(post.serialize()), 200
    return jsonify({'message': 'Post no encontrado'}), 404

@app.route('/posts', methods=['POST'])
def create_post():
    data = request.get_json()
    new_post = Post(user_id=data['user_id'])
    db.session.add(new_post)
    db.session.commit()
    return jsonify(new_post.serialize()), 201

@app.route('/posts/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    post = Post.query.get(post_id)
    if not post:
        return jsonify({'message': 'Post no encontrado'}), 404

    data = request.get_json()
    post.user_id = data.get('user_id', post.user_id)
    db.session.commit()
    return jsonify(post.serialize()), 200

@app.route('/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    post = Post.query.get(post_id)
    if not post:
        return jsonify({'message': 'Post no encontrado'}), 404

    db.session.delete(post)
    db.session.commit()
    return jsonify({'message': 'Post eliminado'}), 200

@app.route('/comments', methods=['GET'])
def get_comments():
    comments = Comment.query.all()
    return jsonify([c.serialize() for c in comments]), 200

@app.route('/comments/<int:comment_id>', methods=['GET'])
def get_comment(comment_id):
    comment = Comment.query.get(comment_id)
    if comment:
        return jsonify(comment.serialize()), 200
    return jsonify({'message': 'Comentario no encontrado'}), 404

@app.route('/comments', methods=['POST'])
def create_comment():
    data = request.get_json()
    new_comment = Comment(
        comment_text=data['comment_text'],
        author_id=data['author_id'],
        post_id=data['post_id']
    )
    db.session.add(new_comment)
    db.session.commit()
    return jsonify(new_comment.serialize()), 201

@app.route('/comments/<int:comment_id>', methods=['PUT'])
def update_comment(comment_id):
    comment = Comment.query.get(comment_id)
    if not comment:
        return jsonify({'message': 'Comentario no encontrado'}), 404

    data = request.get_json()
    comment.comment_text = data.get('comment_text', comment.comment_text)
    comment.author_id = data.get('author_id', comment.author_id)
    comment.post_id = data.get('post_id', comment.post_id)
    db.session.commit()
    return jsonify(comment.serialize()), 200

@app.route('/comments/<int:comment_id>', methods=['DELETE'])
def delete_comment(comment_id):
    comment = Comment.query.get(comment_id)
    if not comment:
        return jsonify({'message': 'Comentario no encontrado'}), 404

    db.session.delete(comment)
    db.session.commit()
    return jsonify({'message': 'Comentario eliminado'}), 200

@app.route('/media', methods=['GET'])
def get_media():
    media_items = Media.query.all()
    return jsonify([m.serialize() for m in media_items]), 200

@app.route('/media/<int:media_id>', methods=['GET'])
def get_single_media(media_id):
    media = Media.query.get(media_id)
    if media:
        return jsonify(media.serialize()), 200
    return jsonify({'message': 'Media no encontrada'}), 404

@app.route('/media', methods=['POST'])
def create_media():
    data = request.get_json()
    new_media = Media(
        type=data['type'],
        url=data['url'],
        post_id=data['post_id']
    )
    db.session.add(new_media)
    db.session.commit()
    return jsonify(new_media.serialize()), 201

@app.route('/media/<int:media_id>', methods=['PUT'])
def update_media(media_id):
    media = Media.query.get(media_id)
    if not media:
        return jsonify({'message': 'Media no encontrada'}), 404

    data = request.get_json()
    media.type = data.get('type', media.type)
    media.url = data.get('url', media.url)
    media.post_id = data.get('post_id', media.post_id)
    db.session.commit()
    return jsonify(media.serialize()), 200

@app.route('/media/<int:media_id>', methods=['DELETE'])
def delete_media(media_id):
    media = Media.query.get(media_id)
    if not media:
        return jsonify({'message': 'Media no encontrada'}), 404

    db.session.delete(media)
    db.session.commit()
    return jsonify({'message': 'Media eliminada'}), 200

@app.route('/followers', methods=['GET'])
def get_followers():
    followers = Follower.query.all()
    return jsonify([f.serialize() for f in followers]), 200

@app.route('/followers', methods=['POST'])
def add_follower():
    data = request.get_json()
    new_follower = Follower(
        user_from_id=data['user_from_id'],
        user_to_id=data['user_to_id']
    )
    db.session.add(new_follower)
    db.session.commit()
    return jsonify(new_follower.serialize()), 201

@app.route('/followers', methods=['DELETE'])
def delete_follower():
    data = request.get_json()
    follower = Follower.query.filter_by(
        user_from_id=data['user_from_id'],
        user_to_id=data['user_to_id']
    ).first()
    if not follower:
        return jsonify({'message': 'Relación no encontrada'}), 404

    db.session.delete(follower)
    db.session.commit()
    return jsonify({'message': 'Relación eliminada'}), 200

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
