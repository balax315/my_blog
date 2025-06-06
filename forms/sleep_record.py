from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField, DateTimeField
from wtforms.validators import DataRequired, Length
from wtforms.fields import DateField, DateTimeLocalField

class SleepRecordForm(FlaskForm):
    date = DateField('记录日期', validators=[DataRequired()])
    sleep_time = DateTimeLocalField('入睡时间', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    wake_time = DateTimeLocalField('起床时间', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    quality = SelectField('睡眠质量', choices=[
        ('good', '优'), 
        ('normal', '良'), 
        ('poor', '差')
    ], validators=[DataRequired()])
    notes = TextAreaField('备注')
    submit = SubmitField('保存')