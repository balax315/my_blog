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

@sleep_bp.route('/sleep-chart')
def sleep_chart():
    return render_template('sleep_chart.html')

@sleep_bp.route('/api/sleep-chart-data')
@login_required
def get_sleep_chart_data():
    # 获取日期范围参数
    start_date_str = request.args.get('start_date', None)
    end_date_str = request.args.get('end_date', None)
    
    # 如果没有提供日期范围，默认使用最近7天
    if not start_date_str or not end_date_str:
        end_date = datetime.datetime.now().date()
        start_date = end_date - datetime.timedelta(days=6)
    else:
        start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d').date()
    
    # 查询指定日期范围内的睡眠记录
    records = SleepRecord.query.filter(
        SleepRecord.user_id == current_user.id,
        SleepRecord.date >= start_date,
        SleepRecord.date <= end_date
    ).order_by(SleepRecord.date).all()
    
    # 格式化记录数据
    formatted_records = []
    total_sleep_minutes = 0
    total_wake_minutes = 0
    total_duration = 0
    
    for record in records:
        # 计算入睡时间（分钟数）
        sleep_hour = record.sleep_time.hour
        sleep_minute = record.sleep_time.minute
        sleep_time_str = f"{sleep_hour:02d}:{sleep_minute:02d}"
        
        # 计算起床时间（分钟数）
        wake_hour = record.wake_time.hour
        wake_minute = record.wake_time.minute
        wake_time_str = f"{wake_hour:02d}:{wake_minute:02d}"
        
        # 累加时间用于计算平均值
        sleep_minutes = sleep_hour * 60 + sleep_minute
        wake_minutes = wake_hour * 60 + wake_minute
        
        # 处理跨天情况
        if record.wake_time.date() > record.sleep_time.date():
            wake_minutes += 24 * 60
        
        total_sleep_minutes += sleep_minutes
        total_wake_minutes += wake_minutes
        total_duration += record.duration
        
        formatted_records.append({
            'id': record.id,
            'date': record.date.strftime('%Y-%m-%d'),
            'sleep_time': sleep_time_str,
            'wake_time': wake_time_str,
            'duration': record.duration,
            'quality': record.quality,
            'notes': record.notes
        })
    
    # 计算平均值
    stats = {}
    if records:
        # 计算平均入睡时间
        avg_sleep_minutes = total_sleep_minutes / len(records)
        avg_sleep_hour = int(avg_sleep_minutes // 60) % 24
        avg_sleep_minute = int(avg_sleep_minutes % 60)
        stats['avg_sleep_time'] = f"{avg_sleep_hour:02d}:{avg_sleep_minute:02d}"
        
        # 计算平均起床时间
        avg_wake_minutes = total_wake_minutes / len(records)
        avg_wake_hour = int(avg_wake_minutes // 60) % 24
        avg_wake_minute = int(avg_wake_minutes % 60)
        stats['avg_wake_time'] = f"{avg_wake_hour:02d}:{avg_wake_minute:02d}"
        
        # 计算平均睡眠时长
        stats['avg_duration'] = total_duration / len(records)
    
    return jsonify({
        'records': formatted_records,
        'stats': stats,
        'date_range': {
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d')
        }
    })