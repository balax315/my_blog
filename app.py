from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf.csrf import CSRFProtect  # 添加这一行导入CSRFProtect
import datetime
from forms import PostForm, SleepRecordForm
import markdown2
import os
from sqlalchemy.sql.expression import extract
from config import config
from models import db, login_manager
from routes import register_blueprints

def create_app(config_name='default'):
    base_dir = os.path.abspath(os.path.dirname(__file__))
    app = Flask(__name__, template_folder=os.path.join(base_dir, 'templates'))
    app.config.from_object(config[config_name])
    
    # 初始化扩展
    db.init_app(app)
    login_manager.init_app(app)
    csrf = CSRFProtect(app)
    
    # 创建 markdown 过滤器
    @app.template_filter('markdown')
    def render_markdown(text):
        return markdown2.markdown(text)
    
    # 注册上下文处理器
    @app.context_processor
    def inject_now():
        return {'now': datetime.datetime.now()}
    
    # 注册蓝图
    register_blueprints(app)
    
    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)


