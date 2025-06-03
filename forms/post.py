from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length

class PostForm(FlaskForm):
    title = StringField('标题', validators=[DataRequired(), Length(max=200)])
    slug = StringField('URL别名', validators=[DataRequired(), Length(max=200)])
    category_id = SelectField('分类', coerce=int)
    content = TextAreaField('内容')  # 不加 validators=[DataRequired()]
    image = FileField('特色图片', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], '只允许上传图片!')
    ])
    submit = SubmitField('保存')