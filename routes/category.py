from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required
from . import category_bp
from models import db, Category, Post

@category_bp.route('/new', methods=['GET', 'POST'])
@login_required
def new_category():
    if request.method == 'POST':
        name = request.form.get('name')
        slug = request.form.get('slug')
        
        if not name or not slug:
            flash('名称和别名不能为空')
        elif Category.query.filter_by(slug=slug).first():
            flash('该别名已存在')
        else:
            category = Category(name=name, slug=slug)
            db.session.add(category)
            try:
                db.session.commit()
                flash('分类已创建')
                return redirect(url_for('admin.admin_categories'))
            except Exception as e:
                db.session.rollback()
                flash(f'创建分类失败: {str(e)}')
    
    return render_template('admin/category_form.html', title='新建分类')

@category_bp.route('/<int:category_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_category(category_id):
    category = Category.query.get_or_404(category_id)
    
    if request.method == 'POST':
        name = request.form.get('name')
        slug = request.form.get('slug')
        
        if not name or not slug:
            flash('名称和别名不能为空')
        elif Category.query.filter(Category.id != category_id, Category.slug == slug).first():
            flash('该别名已存在')
        else:
            category.name = name
            category.slug = slug
            try:
                db.session.commit()
                flash('分类已更新')
                return redirect(url_for('admin.admin_categories'))
            except Exception as e:
                db.session.rollback()
                flash(f'更新分类失败: {str(e)}')
    
    return render_template('admin/category_form.html', category=category, title='编辑分类')

@category_bp.route('/<int:category_id>/delete', methods=['POST'])
@login_required
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    if Post.query.filter_by(category_id=category_id).first():
        flash('该分类下还有文章，无法删除')
        return redirect(url_for('admin.admin_categories'))
    
    try:
        db.session.delete(category)
        db.session.commit()
        flash('分类已删除')
    except Exception as e:
        db.session.rollback()
        flash(f'删除分类失败: {str(e)}')
    
    return redirect(url_for('admin.admin_categories'))