from flask import render_template, request, redirect, url_for, flash, current_app, jsonify
from flask_login import login_required
import os
from . import admin_bp
from models import db, Post, Category
from forms import PostForm, IndexContentForm
import markdown2
from werkzeug.utils import secure_filename
import uuid

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
                
                # 处理图片上传
                if form.image.data:
                    image_filename = save_image(form.image.data)
                    post.image_filename = image_filename
                
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
        
        # 处理图片上传
        if form.image.data:
            # 如果有旧图片，删除它
            if post.image_filename:
                try:
                    old_image_path = os.path.join(current_app.root_path, 'static', 'uploads', post.image_filename)
                    if os.path.exists(old_image_path):
                        os.remove(old_image_path)
                except Exception as e:
                    print(f"删除旧图片失败: {str(e)}")
            
            # 保存新图片
            image_filename = save_image(form.image.data)
            post.image_filename = image_filename
        
        db.session.commit()
        flash('文章已更新')
        return redirect(url_for('admin.dashboard'))
    
    return render_template('admin/post_form.html', form=form, title='编辑文章', post=post)

# 辅助函数：保存上传的图片
def save_image(image_file):
    # 生成安全的文件名
    filename = secure_filename(image_file.filename)
    # 添加唯一标识符，避免文件名冲突
    unique_filename = f"{uuid.uuid4().hex}_{filename}"
    # 保存路径
    upload_path = os.path.join(current_app.root_path, 'static', 'uploads')
    # 确保目录存在
    os.makedirs(upload_path, exist_ok=True)
    # 保存文件
    image_file.save(os.path.join(upload_path, unique_filename))
    return unique_filename

@admin_bp.route('/categories')
@login_required
def admin_categories():
    categories = Category.query.all()
    return render_template('admin/categories.html', categories=categories)

@admin_bp.route('/edit-index', methods=['GET', 'POST'])
@login_required
def edit_index():
    form = IndexContentForm()
    index_md_path = os.path.join(current_app.root_path, 'templates', 'index.md')
    index_html_path = os.path.join(current_app.root_path, 'templates', 'index.html')
    
    if request.method == 'POST' and form.validate_on_submit():
        content = form.content.data
        try:
            # 保存Markdown内容
            with open(index_md_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            # 转换为HTML并保存，启用多种extras
            html_content = markdown2.markdown(
                content,
                extras=[
                    "fenced-code-blocks",
                    "tables",
                    "header-ids",
                    "task_list",
                    "footnotes",
                    "cuddled-lists",
                    "code-friendly",
                    "smarty-pants"
                ]
            )
            
            # 将HTML内容嵌入到模板中，注意添加了markdown-content类
            template_content = f'{{% extends "base.html" %}}{{% block content %}}<div class="markdown-content">{html_content}</div>{{% endblock %}}'
            
            with open(index_html_path, 'w', encoding='utf-8') as f:
                f.write(template_content)
                
            flash('首页内容已更新')
            return redirect(url_for('admin.dashboard'))
        except Exception as e:
            flash(f'更新失败: {str(e)}')
    
    # 读取现有的Markdown内容
    try:
        if os.path.exists(index_md_path):
            with open(index_md_path, 'r', encoding='utf-8') as f:
                form.content.data = f.read()
        else:
            # 如果Markdown文件不存在，尝试从HTML提取内容
            with open(index_html_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
                # 这里简单处理，实际可能需要更复杂的HTML到Markdown转换
                # 提取content块中的内容
                start_tag = '{%% block content %%}'
                end_tag = '{%% endblock %%}'
                start_pos = html_content.find(start_tag) + len(start_tag)
                end_pos = html_content.find(end_tag)
                if start_pos > 0 and end_pos > start_pos:
                    form.content.data = html_content[start_pos:end_pos].strip()
                else:
                    form.content.data = '# 欢迎来到我的博客\n\n这是首页内容，请使用Markdown编辑。'
    except Exception as e:
        form.content.data = '# 欢迎来到我的博客\n\n这是首页内容，请使用Markdown编辑。'
        flash(f'读取文件失败: {str(e)}')
    
    return render_template('admin/edit_index.html', form=form)

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


@admin_bp.route('/upload-image', methods=['POST'])
@login_required
def upload_image():
    if 'image' not in request.files:
        return jsonify({'error': '没有文件'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400
    
    if file and allowed_file(file.filename):
        filename = save_image(file)
        image_url = url_for('static', filename=f'uploads/{filename}')
        return jsonify({'url': image_url})
    
    return jsonify({'error': '不支持的文件类型'}), 400

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}