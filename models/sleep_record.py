import datetime
from . import db

class SleepRecord(db.Model):
    __tablename__ = 'sleep_records'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    sleep_time = db.Column(db.DateTime, nullable=False)
    wake_time = db.Column(db.DateTime, nullable=False)
    quality = db.Column(db.Enum('good', 'normal', 'poor'), nullable=False)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('sleep_records', lazy=True))
    
    @property
    def duration(self):
        """计算睡眠时长（小时）"""
        delta = self.wake_time - self.sleep_time
        return round(delta.total_seconds() / 3600, 1)