from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
from forms import PostForm
import markdown2  # 导入 markdown2
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost/blog_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['TEMPLATES_AUTO_RELOAD'] = True   # 添加这行来禁用模板缓存


# 创建 markdown 过滤器
@app.template_filter('markdown')
def render_markdown(text):
    return markdown2.markdown(text)  # 直接调用 markdown2.markdown 函数

# 删除错误的初始化行: Markdown(app)

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# 模型定义
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(80))
    bio = db.Column(db.Text)
    avatar = db.Column(db.String(200))
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    slug = db.Column(db.String(50), unique=True, nullable=False)
    posts = db.relationship('Post', backref='category', lazy=True)

class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 路由
@app.route('/')
def index():
    # 按年份分组获取文章
    posts_by_year = {}
    posts = Post.query.order_by(Post.created_at.desc()).all()
    
    for post in posts:
        year = post.created_at.year
        if year not in posts_by_year:
            posts_by_year[year] = []
        posts_by_year[year].append(post)
    
    # 按年份降序排序
    sorted_years = sorted(posts_by_year.keys(), reverse=True)
    
    return render_template('index.html', posts_by_year=posts_by_year, years=sorted_years)

@app.route('/articles')
def articles():
    # 按年份分组获取文章
    posts_by_year = {}
    posts = Post.query.order_by(Post.created_at.desc()).all()
    
    for post in posts:
        year = post.created_at.year
        if year not in posts_by_year:
            posts_by_year[year] = []
        posts_by_year[year].append(post)
    
    # 按年份降序排序
    sorted_years = sorted(posts_by_year.keys(), reverse=True)
    
    return render_template('articles.html', posts_by_year=posts_by_year, years=sorted_years)

@app.route('/article/<slug>')
def article(slug):
    post = Post.query.filter_by(slug=slug).first_or_404()
    return render_template('article.html', post=post)

@app.route('/category/<slug>')
def category(slug):
    category = Category.query.filter_by(slug=slug).first_or_404()
       # 按年份分组获取文章
    posts_by_year = {}
    posts = Post.query.filter_by(category_id=category.id).order_by(Post.created_at.desc()).all()
    
    for post in posts:
        year = post.created_at.year
        if year not in posts_by_year:
            posts_by_year[year] = []
        posts_by_year[year].append(post)
    # 按年份降序排序
    sorted_years = sorted(posts_by_year.keys(), reverse=True)
    
    return render_template('category.html', category=category,posts_by_year=posts_by_year, years=sorted_years)

 

@app.route('/search')
def search():
    query = request.args.get('q', '')
    if query:
        posts = Post.query.filter(Post.title.contains(query) | Post.content.contains(query)).all()
    else:
        posts = []
    return render_template('search.html', posts=posts, query=query)

# 管理员路由
@app.route('/admin/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('admin_dashboard'))
        
        flash('用户名或密码错误')
    
    return render_template('admin/login.html')

@app.route('/admin/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/admin')
@login_required
def admin_dashboard():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template('admin/dashboard.html', posts=posts)



@app.route('/admin/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    form.category_id.choices = [(c.id, c.name) for c in Category.query.all()]
    if request.method == 'POST':
        print("表单已提交")
        print(f"表单数据: {request.form}")
        # 确保表单验证时考虑到POST数据

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
                    return redirect(url_for('admin_dashboard'))
                except Exception as e:
                    db.session.rollback()
                    flash(f'创建文章失败: {str(e)}')
                    print(f"数据库错误: {str(e)}")
        else:
            print(f"表单验证错误: {form.errors}")

    
    return render_template('admin/post_form.html', form=form, title='新建文章')

@app.route('/admin/post/<int:post_id>/edit', methods=['GET', 'POST'])
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
        return redirect(url_for('admin_dashboard'))
    
    return render_template('admin/post_form.html', form=form, title='编辑文章', post=post)  # 添加 post=post

@app.route('/admin/categories')
@login_required
def admin_categories():
    categories = Category.query.all()
    return render_template('admin/categories.html', categories=categories)

@app.route('/admin/category/new', methods=['GET', 'POST'])
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
                return redirect(url_for('admin_categories'))
            except Exception as e:
                db.session.rollback()
                flash(f'创建分类失败: {str(e)}')
    
    return render_template('admin/category_form.html', title='新建分类')

@app.route('/admin/category/<int:category_id>/edit', methods=['GET', 'POST'])
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
                return redirect(url_for('admin_categories'))
            except Exception as e:
                db.session.rollback()
                flash(f'更新分类失败: {str(e)}')
    
    return render_template('admin/category_form.html', category=category, title='编辑分类')

@app.route('/admin/category/<int:category_id>/delete', methods=['POST'])
@login_required
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    if Post.query.filter_by(category_id=category_id).first():
        flash('该分类下还有文章，无法删除')
        return redirect(url_for('admin_categories'))
    
    try:
        db.session.delete(category)
        db.session.commit()
        flash('分类已删除')
    except Exception as e:
        db.session.rollback()
        flash(f'删除分类失败: {str(e)}')
    
    return redirect(url_for('admin_categories'))

@app.route('/admin/edit-index', methods=['GET', 'POST'])
@login_required
def edit_index():
    index_path = os.path.join(app.root_path, 'templates', 'index.html')
    
    if request.method == 'POST':
        content = request.form.get('content')
        try:
            with open(index_path, 'w', encoding='utf-8') as f:
                f.write(content)
            flash('首页内容已更新')
            return redirect(url_for('admin_dashboard'))
        except Exception as e:
            flash(f'更新失败: {str(e)}')
    
    try:
        with open(index_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        content = ''
        flash(f'读取文件失败: {str(e)}')
    
    return render_template('admin/edit_index.html', content=content)


@app.context_processor
def inject_now():
    return {'now': datetime.datetime.now()}



if __name__ == '__main__':
    app.run(debug=True)


