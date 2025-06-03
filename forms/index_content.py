from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length

class IndexContentForm(FlaskForm):
    content = TextAreaField('Markdown 内容')
    submit = SubmitField('保存')