from app import app, db, User, Category, Post
import datetime

# 在应用上下文中创建表
with app.app_context():
    # 创建所有表
    db.create_all()
    
    # 检查是否已存在管理员用户
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        # 创建管理员用户
        admin = User(username='admin', name='管理员')
        admin.set_password('admin123')  # 设置初始密码
        db.session.add(admin)
    
    # 创建示例分类
    categories = {
        'python': '编程',
        'life': '生活',
        'tech': '技术'
    }
    
    for slug, name in categories.items():
        if not Category.query.filter_by(slug=slug).first():
            category = Category(name=name, slug=slug)
            db.session.add(category)
    
    # 提交更改
    db.session.commit()
    
    # 获取分类
    python_category = Category.query.filter_by(slug='python').first()
    life_category = Category.query.filter_by(slug='life').first()
    tech_category = Category.query.filter_by(slug='tech').first()
    
    # 创建示例文章
    sample_posts = [
        {
            'title': '2024 年总结',
            'slug': '2024-summary',
            'content': '<p>这是2024年的总结文章内容...</p>',
            'created_at': datetime.datetime(2024, 3, 21),
            'category': python_category
        },
        {
            'title': '代码屋开源 x PyCon China 2024',
            'slug': 'pycon-china-2024',
            'content': '<p>这是关于PyCon China 2024的文章内容...</p>',
            'created_at': datetime.datetime(2024, 11, 10),
            'category': python_category
        },
        {
            'title': '一辆自行车多久会被偷',
            'slug': 'bike-stolen',
            'content': '<p>这是关于自行车被偷的文章内容...</p>',
            'created_at': datetime.datetime(2024, 10, 28),
            'category': life_category
        },
        {
            'title': '夏天不是读书天',
            'slug': 'summer-not-for-reading',
            'content': '<p>这是关于夏天不适合读书的文章内容...</p>',
            'created_at': datetime.datetime(2024, 2, 25),
            'category': life_category
        },
        {
            'title': '干杯',
            'slug': 'cheers',
            'content': '<p>这是关于干杯的文章内容...</p>',
            'created_at': datetime.datetime(2024, 1, 28),
            'category': life_category
        },
        {
            'title': 'Flask 已死，FastAPI 永生',
            'slug': 'flask-dead-fastapi-alive',
            'content': '<p>这是关于Flask和FastAPI的文章内容...</p>',
            'created_at': datetime.datetime(2023, 12, 23),
            'category': tech_category
        }
    ]
    
    # 添加示例文章
    for post_data in sample_posts:
        if not Post.query.filter_by(slug=post_data['slug']).first():
            post = Post(
                title=post_data['title'],
                slug=post_data['slug'],
                content=post_data['content'],
                created_at=post_data['created_at'],
                category=post_data['category']
            )
            db.session.add(post)
    
    # 提交更改
    db.session.commit()
    
    print('数据库初始化完成！')