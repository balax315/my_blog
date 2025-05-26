from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length

class PostForm(FlaskForm):
    title = StringField('标题', validators=[DataRequired(), Length(max=200)])
    slug = StringField('URL别名', validators=[DataRequired(), Length(max=200)])
    category_id = SelectField('分类', coerce=int)
    content = TextAreaField('内容')  # 不加 validators=[DataRequired()]
    submit = SubmitField('保存')