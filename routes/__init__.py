from flask import Blueprint

# 创建蓝图
main_bp = Blueprint('main', __name__)
auth_bp = Blueprint('auth', __name__, url_prefix='/admin')
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
category_bp = Blueprint('category', __name__, url_prefix='/admin/category')
sleep_bp = Blueprint('sleep', __name__)

# 导入路由
from . import main, auth, admin, category, sleep

def register_blueprints(app):
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(category_bp)
    app.register_blueprint(sleep_bp)