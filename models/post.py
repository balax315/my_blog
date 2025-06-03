import datetime
from . import db

class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    content = db.Column(db.Text)
    image_filename = db.Column(db.String(100))  # 存储图片文件名
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))