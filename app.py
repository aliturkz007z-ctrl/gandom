from flask import Flask, render_template, request, jsonify, send_from_directory, session, redirect, url_for
from flask_cors import CORS
import json
import os
from datetime import datetime
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
CORS(app)

# Create data directory if it doesn't exist
if not os.path.exists('data'):
    os.makedirs('data')

DATA_FILE = 'data/storage.json'
PASSWORD = 'AG001'

def load_data():
    """Load data from JSON file"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {
        'kissCount': 0,
        'gallery': [],
        'notes': [],
        'todos': [],
        'chats': [],
        'music': []
    }

def save_data(data):
    """Save data to JSON file"""
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Error saving data: {e}")
        return False

@app.route('/')
def index():
    """Main page - redirect to login if not authenticated"""
    if 'authenticated' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        password = request.json.get('password')
        if password == PASSWORD:
            session['authenticated'] = True
            return jsonify({'success': True})
        return jsonify({'success': False, 'message': 'رمز اشتباه است!'})
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logout"""
    session.pop('authenticated', None)
    return redirect(url_for('login'))

@app.route('/api/kiss', methods=['GET', 'POST'])
def kiss():
    """Kiss counter API"""
    data = load_data()
    
    if request.method == 'POST':
        action = request.json.get('action')
        if action == 'add':
            data['kissCount'] = data.get('kissCount', 0) + 1
        elif action == 'reset':
            data['kissCount'] = 0
        save_data(data)
    
    return jsonify({'success': True, 'count': data.get('kissCount', 0)})

@app.route('/api/gallery', methods=['GET', 'POST', 'DELETE'])
def gallery():
    """Gallery API"""
    data = load_data()
    
    if request.method == 'POST':
        action = request.json.get('action')
        
        if action == 'add':
            item = {
                'id': int(datetime.now().timestamp() * 1000),
                'image': request.json.get('image'),
                'caption': request.json.get('caption', ''),
                'date': datetime.now().strftime('%Y/%m/%d - %H:%M'),
                'comments': []
            }
            if 'gallery' not in data:
                data['gallery'] = []
            data['gallery'].insert(0, item)
            save_data(data)
            return jsonify({'success': True, 'message': 'عکس اضافه شد'})
        
        elif action == 'comment':
            item_id = request.json.get('id')
            comment = request.json.get('comment')
            
            if 'gallery' not in data:
                data['gallery'] = []
            
            for item in data['gallery']:
                if item['id'] == item_id:
                    if 'comments' not in item:
                        item['comments'] = []
                    item['comments'].append({
                        'text': comment,
                        'date': datetime.now().strftime('%Y/%m/%d - %H:%M')
                    })
                    save_data(data)
                    return jsonify({'success': True, 'message': 'کامنت اضافه شد'})
            
            return jsonify({'success': False, 'message': 'عکس پیدا نشد'})
    
    elif request.method == 'DELETE':
        item_id = request.json.get('id')
        if 'gallery' not in data:
            data['gallery'] = []
        data['gallery'] = [item for item in data['gallery'] if item['id'] != item_id]
        save_data(data)
        return jsonify({'success': True, 'message': 'عکس حذف شد'})
    
    return jsonify({'success': True, 'gallery': data.get('gallery', [])})

@app.route('/api/notes', methods=['GET', 'POST', 'DELETE'])
def notes():
    """Notes API"""
    data = load_data()
    
    if request.method == 'POST':
        note = {
            'id': int(datetime.now().timestamp() * 1000),
            'text': request.json.get('text'),
            'date': datetime.now().strftime('%Y/%m/%d - %H:%M')
        }
        if 'notes' not in data:
            data['notes'] = []
        data['notes'].insert(0, note)
        save_data(data)
        return jsonify({'success': True, 'message': 'یادداشت ذخیره شد'})
    
    elif request.method == 'DELETE':
        note_id = request.json.get('id')
        if 'notes' not in data:
            data['notes'] = []
        data['notes'] = [note for note in data['notes'] if note['id'] != note_id]
        save_data(data)
        return jsonify({'success': True, 'message': 'یادداشت حذف شد'})
    
    return jsonify({'success': True, 'notes': data.get('notes', [])})

@app.route('/api/todos', methods=['GET', 'POST', 'PUT', 'DELETE'])
def todos():
    """Todos API"""
    data = load_data()
    
    if 'todos' not in data:
        data['todos'] = []
    
    if request.method == 'POST':
        todo = {
            'id': int(datetime.now().timestamp() * 1000),
            'text': request.json.get('text'),
            'completed': False,
            'date': datetime.now().strftime('%Y/%m/%d')
        }
        data['todos'].append(todo)
        save_data(data)
        return jsonify({'success': True, 'message': 'کار اضافه شد'})
    
    elif request.method == 'PUT':
        todo_id = request.json.get('id')
        for todo in data['todos']:
            if todo['id'] == todo_id:
                todo['completed'] = not todo.get('completed', False)
                save_data(data)
                return jsonify({'success': True, 'message': 'وضعیت تغییر کرد'})
        return jsonify({'success': False, 'message': 'کار پیدا نشد'})
    
    elif request.method == 'DELETE':
        todo_id = request.json.get('id')
        data['todos'] = [t for t in data['todos'] if t['id'] != todo_id]
        save_data(data)
        return jsonify({'success': True, 'message': 'کار حذف شد'})
    
    return jsonify({'success': True, 'todos': data['todos']})

@app.route('/api/chats', methods=['GET', 'POST', 'DELETE'])
def chats():
    """Chat API"""
    data = load_data()
    
    if 'chats' not in data:
        data['chats'] = []
    
    if request.method == 'POST':
        chat = {
            'id': int(datetime.now().timestamp() * 1000),
            'sender': request.json.get('sender'),  # 'ali' or 'gandom'
            'message': request.json.get('message'),
            'time': datetime.now().strftime('%H:%M')
        }
        data['chats'].append(chat)
        save_data(data)
        return jsonify({'success': True, 'message': 'پیام ارسال شد'})
    
    elif request.method == 'DELETE':
        action = request.json.get('action')
        if action == 'clear':
            data['chats'] = []
            save_data(data)
            return jsonify({'success': True, 'message': 'چت‌ها پاک شدند'})
        else:
            chat_id = request.json.get('id')
            data['chats'] = [chat for chat in data['chats'] if chat['id'] != chat_id]
            save_data(data)
            return jsonify({'success': True, 'message': 'پیام حذف شد'})
    
    return jsonify({'success': True, 'chats': data['chats']})

@app.route('/api/music', methods=['GET', 'POST', 'DELETE'])
def music():
    """Music API"""
    data = load_data()
    
    if 'music' not in data:
        data['music'] = []
    
    if request.method == 'POST':
        song = {
            'id': int(datetime.now().timestamp() * 1000),
            'title': request.json.get('title'),
            'artist': request.json.get('artist', 'نامشخص'),
            'file': request.json.get('file'),
            'date': datetime.now().strftime('%Y/%m/%d')
        }
        data['music'].append(song)
        save_data(data)
        return jsonify({'success': True, 'message': 'آهنگ اضافه شد'})
    
    elif request.method == 'DELETE':
        song_id = request.json.get('id')
        data['music'] = [song for song in data['music'] if song['id'] != song_id]
        save_data(data)
        return jsonify({'success': True, 'message': 'آهنگ حذف شد'})
    
    return jsonify({'success': True, 'music': data['music']})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=True)
