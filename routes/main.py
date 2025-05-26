from flask import render_template, request
from . import main_bp
from models import Post, Category

@main_bp.route('/')
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

@main_bp.route('/articles')
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

@main_bp.route('/article/<slug>')
def article(slug):
    post = Post.query.filter_by(slug=slug).first_or_404()
    return render_template('article.html', post=post)

@main_bp.route('/category/<slug>')
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
    
    return render_template('category.html', category=category, posts_by_year=posts_by_year, years=sorted_years)

@main_bp.route('/search')
def search():
    query = request.args.get('q', '')
    if query:
        posts = Post.query.filter(Post.title.contains(query) | Post.content.contains(query)).all()
    else:
        posts = []
    return render_template('search.html', posts=posts, query=query)