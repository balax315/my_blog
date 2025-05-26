from flask import render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required
import os
from . import admin_bp
from models import db, Post, Category
from forms import PostForm

@admin_bp.route('/')
@login_required
def dashboard():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template('admin/dashboard.html', posts=posts)

@admin_bp.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    form.category_id.choices = [(c.id, c.name) for c in Category.query.all()]
    if request.method == 'POST':
        print("表单已提交")
        print(f"表单数据: {request.form}")

        if form.validate_on_submit():
            if not form.content.data.strip():
                flash('内容不能为空')
            elif Post.query.filter_by(slug=form.slug.data).first():
                flash('Slug 已存在，请使用其他 slug')
            else:
                post = Post(
                    title=form.title.data,
                    slug=form.slug.data,
                    content=form.content.data,
                    category_id=form.category_id.data
                )
                db.session.add(post)
                try:
                    db.session.commit()
                    flash('文章已创建')
                    return redirect(url_for('admin.dashboard'))
                except Exception as e:
                    db.session.rollback()
                    flash(f'创建文章失败: {str(e)}')
                    print(f"数据库错误: {str(e)}")
        else:
            print(f"表单验证错误: {form.errors}")

    return render_template('admin/post_form.html', form=form, title='新建文章')

@admin_bp.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    form = PostForm(obj=post)
    form.category_id.choices = [(c.id, c.name) for c in Category.query.all()]
    
    if form.validate_on_submit():
        post.title = form.title.data
        post.slug = form.slug.data
        post.content = form.content.data
        post.category_id = form.category_id.data
        db.session.commit()
        flash('文章已更新')
        return redirect(url_for('admin.dashboard'))
    
    return render_template('admin/post_form.html', form=form, title='编辑文章', post=post)

@admin_bp.route('/categories')
@login_required
def admin_categories():
    categories = Category.query.all()
    return render_template('admin/categories.html', categories=categories)

@admin_bp.route('/edit-index', methods=['GET', 'POST'])
@login_required
def edit_index():
    index_path = os.path.join(current_app.root_path, 'templates', 'index.html')
    
    if request.method == 'POST':
        content = request.form.get('content')
        try:
            with open(index_path, 'w', encoding='utf-8') as f:
                f.write(content)
            flash('首页内容已更新')
            return redirect(url_for('admin.dashboard'))
        except Exception as e:
            flash(f'更新失败: {str(e)}')
    
    try:
        with open(index_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        content = ''
        flash(f'读取文件失败: {str(e)}')
    
    return render_template('admin/edit_index.html', content=content)

@admin_bp.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    try:
        db.session.delete(post)
        db.session.commit()
        flash('文章已删除')
    except Exception as e:
        db.session.rollback()
        flash(f'删除失败: {str(e)}')
    return redirect(url_for('admin.dashboard'))