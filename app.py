from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
from datetime import datetime, timedelta
import os
from functools import wraps
from models import Database
from ai_chat import TCMAIChat
from knowledge_base import KnowledgeBase
import config

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
CORS(app)

db = Database(config.DATABASE_PATH)
kb = KnowledgeBase(config.KNOWLEDGE_PATH)
ai = TCMAIChat()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': '请先登录'}), 401
        return f(*args, **kwargs)
    return decorated_function

def get_client_ip():
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0]
    return request.remote_addr

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('chat_page'))
    return render_template('index.html')

@app.route('/chat')
@login_required
def chat_page():
    return render_template('chat.html')

@app.route('/profile')
@login_required
def profile_page():
    return render_template('profile.html')

@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.json
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        phone = data.get('phone', '').strip()
        
        if not username or not password or not phone:
            return jsonify({'success': False, 'message': '请填写完整信息'})
        
        if len(username) < 3 or len(username) > 20:
            return jsonify({'success': False, 'message': '用户名长度3-20个字符'})
        
        if len(password) < 6:
            return jsonify({'success': False, 'message': '密码至少6个字符'})
        
        if len(phone) != 11 or not phone.isdigit():
            return jsonify({'success': False, 'message': '请输入正确的手机号'})
        
        ip = get_client_ip()
        if not db.check_ip_register_limit(ip):
            return jsonify({'success': False, 'message': '该IP今日注册次数已达上限'})
        
        success, message, user_id = db.create_user(username, password, phone, ip)
        
        if success:
            session['user_id'] = user_id
            session['username'] = username
            session.permanent = True
            return jsonify({'success': True, 'message': '注册成功'})
        else:
            return jsonify({'success': False, 'message': message})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'注册失败: {str(e)}'})

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.json
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        
        if not username or not password:
            return jsonify({'success': False, 'message': '请输入用户名和密码'})
        
        success, message, user_data = db.verify_user(username, password)
        
        if success:
            session['user_id'] = user_data['id']
            session['username'] = user_data['username']
            session.permanent = True
            
            db.update_last_login(user_data['id'])
            
            return jsonify({'success': True, 'message': '登录成功'})
        else:
            return jsonify({'success': False, 'message': message})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'登录失败: {str(e)}'})

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True, 'message': '已退出登录'})

@app.route('/api/check_auth', methods=['GET'])
def check_auth():
    if 'user_id' in session:
        return jsonify({
            'authenticated': True,
            'username': session.get('username')
        })
    return jsonify({'authenticated': False})

@app.route('/api/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user_id = session['user_id']
    
    if request.method == 'GET':
        profile_data = db.get_profile(user_id)
        return jsonify({'success': True, 'profile': profile_data})
    
    else:
        try:
            data = request.json
            age = int(data.get('age', 0))
            gender = data.get('gender', '').strip()
            constitution = data.get('constitution', '').strip()
            location = data.get('location', '').strip()
            
            if age < 1 or age > 120:
                return jsonify({'success': False, 'message': '请输入有效的年龄'})
            
            if not gender or not constitution or not location:
                return jsonify({'success': False, 'message': '请填写完整信息'})
            
            db.save_profile(user_id, age, gender, constitution, location)
            return jsonify({'success': True, 'message': '档案保存成功'})
            
        except Exception as e:
            return jsonify({'success': False, 'message': f'保存失败: {str(e)}'})

@app.route('/api/usage', methods=['GET'])
@login_required
def usage():
    user_id = session['user_id']
    today_usage = db.get_today_usage(user_id)
    limit = config.FREE_DAILY_LIMIT
    
    return jsonify({
        'success': True,
        'usage': today_usage,
        'limit': limit,
        'remaining': max(0, limit - today_usage)
    })

@app.route('/api/chat', methods=['POST'])
@login_required
def chat():
    try:
        user_id = session['user_id']
        data = request.json
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({'success': False, 'message': '消息不能为空'})
        
        can_use, count = db.check_daily_limit(user_id, config.FREE_DAILY_LIMIT)
        if not can_use:
            return jsonify({
                'success': False,
                'message': f'今日使用次数已达上限({config.FREE_DAILY_LIMIT}次)',
                'limit_reached': True
            })
        
        ip = get_client_ip()
        user_agent = request.headers.get('User-Agent', '')
        db.log_usage(user_id, ip, user_agent)
        
        profile = db.get_profile(user_id)
        knowledge_results = kb.search(message)
        knowledge_text = kb.format_knowledge(knowledge_results)
        conversations = db.get_conversations(user_id, limit=5)
        
        success, response = ai.chat(message, profile, knowledge_text, conversations)
        
        if success:
            db.save_conversation(user_id, message, response)
            return jsonify({
                'success': True,
                'response': response,
                'usage': count,
                'limit': config.FREE_DAILY_LIMIT
            })
        else:
            return jsonify({'success': False, 'message': response})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'发生错误: {str(e)}'})

@app.route('/api/conversations', methods=['GET'])
@login_required
def conversations():
    user_id = session['user_id']
    limit = request.args.get('limit', 10, type=int)
    
    convs = db.get_conversations(user_id, limit=limit)
    return jsonify({'success': True, 'conversations': convs})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
