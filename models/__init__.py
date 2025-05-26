from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

# 导入所有模型，使它们在其他地方可用
from .user import User
from .category import Category
from .post import Post
from .sleep_record import SleepRecord

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))