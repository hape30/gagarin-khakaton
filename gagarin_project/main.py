import sqlite3
from flask import Flask, g, request
from flask_restful import Api, Resource
import os
from sqlite3 import Error

app = Flask(__name__)
api = Api(app)

DATABASE = 'videos.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

class VideoUpload(Resource):
    def post(self):
        db = get_db()
        c = db.cursor()

        if 'file' not in request.files:
            return {'message': 'No file part'}, 400

        file = request.files['file']

        if file.filename == '':
            return {'message': 'No selected file'}, 400

        if file.mimetype.split('/')[0]!= 'video':
            return {'message': 'Invalid file type. Only video files are allowed'}, 400

        # Чтение содержимого файла в виде bytes
        file_content = file.read()

        # Сохранение содержимого файла в базу данных
        c.execute('INSERT INTO videos (filename, file_data) VALUES (?, ?)', (file.filename, file_content))
        db.commit()

        video_id = c.lastrowid
        return {'message': 'Video uploaded successfully', 'video_id': video_id}, 200




class Video(Resource):
    def get(self, video_id):
        db = get_db()
        c = db.cursor()

        c.execute('SELECT * FROM videos WHERE video_id =?', (video_id,))
        video = c.fetchone()

        if video is None:
            return {'message': 'Video not found'}, 404

        return {'video_id': video[0], 'filename': video[1]}, 200

    def put(self, video_id):
        db = get_db()
        c = db.cursor()
        
        c.execute('SELECT * FROM videos WHERE video_id =?', (video_id,))
        video = c.fetchone()

        if video is None:
            return {'message': 'Video not found'}, 404

        # Здесь можно добавить код для обновления информации о видео файле

        db.commit()
        return {'message': 'Video updated successfully'}, 200

    def delete(self, video_id):
        db = get_db()
        c = db.cursor()

        c.execute('DELETE FROM videos WHERE video_id =?', (video_id,))
        db.commit()

        return {'message': 'Video deleted successfully'}, 200

api.add_resource(VideoUpload, '/upload')
api.add_resource(Video, '/video/<int:video_id>')

conn = sqlite3.connect(DATABASE)
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS videos (
    video_id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    file_path TEXT NOT NULL)''')

if __name__ == '__main__':
    app.run()