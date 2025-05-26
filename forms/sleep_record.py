from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField, TimeField
from wtforms.validators import DataRequired, Length
from wtforms.fields import DateField

class SleepRecordForm(FlaskForm):
    date = DateField('日期', validators=[DataRequired()])
    sleep_time = TimeField('入睡时间', validators=[DataRequired()])
    wake_time = TimeField('起床时间', validators=[DataRequired()])
    quality = SelectField('睡眠质量', choices=[
        ('good', '优'), 
        ('normal', '良'), 
        ('poor', '差')
    ], validators=[DataRequired()])
    notes = TextAreaField('备注')
    submit = SubmitField('保存')