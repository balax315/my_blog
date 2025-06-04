from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
import datetime
from sqlalchemy.sql.expression import extract
from . import sleep_bp
from models import db, SleepRecord
from forms import SleepRecordForm

@sleep_bp.route('/sleep-calendar')
def sleep_calendar():
    current_year = datetime.datetime.now().year
    return render_template('sleep_calendar.html', year=current_year)

@sleep_bp.route('/api/sleep-records')
@login_required
def get_sleep_records():
    year = request.args.get('year', datetime.datetime.now().year, type=int)
    records = SleepRecord.query.filter(
        SleepRecord.user_id == current_user.id,
        extract('year', SleepRecord.date) == year
    ).all()
    
    # 添加调试输出
    print(f"Found {len(records)} records for year {year}")
    
    data = [{
        'id': record.id,
        'date': record.date.strftime('%Y-%m-%d'),
        'sleep_time': record.sleep_time.strftime('%H:%M'),
        'wake_time': record.wake_time.strftime('%H:%M'),
        'duration': record.duration,
        'quality': record.quality,
        'notes': record.notes
    } for record in records]
    
    # 添加调试输出
    print(f"Returning data: {data}")
    
    return jsonify(data)

@sleep_bp.route('/admin/sleep-record/new', methods=['GET', 'POST'])
@login_required
def new_sleep_record():
    form = SleepRecordForm()
    if form.validate_on_submit():
        # 将日期和时间合并为datetime对象
        sleep_datetime = datetime.datetime.combine(form.date.data, form.sleep_time.data)
        wake_datetime = datetime.datetime.combine(form.date.data, form.wake_time.data)
        
        # 如果起床时间早于入睡时间，说明跨天了，需要加一天
        if wake_datetime < sleep_datetime:
            wake_datetime = wake_datetime + datetime.timedelta(days=1)
            
        record = SleepRecord(
            user_id=current_user.id,
            date=form.date.data,
            sleep_time=sleep_datetime,
            wake_time=wake_datetime,
            quality=form.quality.data,
            notes=form.notes.data
        )
        db.session.add(record)
        try:
            db.session.commit()
            flash('睡眠记录已添加')
            return redirect(url_for('sleep.sleep_calendar'))
        except Exception as e:
            db.session.rollback()
            flash(f'添加失败: {str(e)}')
    
    return render_template('admin/sleep_record_form.html', form=form, title='添加睡眠记录')

@sleep_bp.route('/admin/sleep-record/<int:record_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_sleep_record(record_id):
    record = SleepRecord.query.get_or_404(record_id)
    if record.user_id != current_user.id:
        flash('无权编辑此记录')
        return redirect(url_for('sleep.sleep_calendar'))
    
    form = SleepRecordForm(obj=record)
    if form.validate_on_submit():
        # 将日期和时间合并为datetime对象
        sleep_datetime = datetime.datetime.combine(form.date.data, form.sleep_time.data)
        wake_datetime = datetime.datetime.combine(form.date.data, form.wake_time.data)
        
        # 如果起床时间早于入睡时间，说明跨天了，需要加一天
        if wake_datetime < sleep_datetime:
            wake_datetime = wake_datetime + datetime.timedelta(days=1)
            
        record.date = form.date.data
        record.sleep_time = sleep_datetime
        record.wake_time = wake_datetime
        record.quality = form.quality.data
        record.notes = form.notes.data
        
        try:
            db.session.commit()
            flash('睡眠记录已更新')
            return redirect(url_for('sleep.sleep_calendar'))
        except Exception as e:
            db.session.rollback()
            flash(f'更新失败: {str(e)}')
    
    return render_template('admin/sleep_record_form.html', form=form, title='编辑睡眠记录')

@sleep_bp.route('/admin/sleep-record/<int:record_id>/delete', methods=['POST'])
@login_required
def delete_sleep_record(record_id):
    record = SleepRecord.query.get_or_404(record_id)
    if record.user_id != current_user.id:
        flash('无权删除此记录')
        return redirect(url_for('sleep.sleep_calendar'))
    
    try:
        db.session.delete(record)
        db.session.commit()
        flash('睡眠记录已删除')
    except Exception as e:
        db.session.rollback()
        flash(f'删除失败: {str(e)}')
    
    return redirect(url_for('sleep.sleep_calendar'))