from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from . import auth_bp
from models import User
from forms import LoginForm  # 改为从forms包直接导入

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('admin.dashboard'))
        
        flash('用户名或密码错误')
    
    return render_template('admin/login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))