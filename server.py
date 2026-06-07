"""
DeepSeek Neural Interface — Flask Backend
Handles: chat backup/load, file upload/parsing, API proxy (streaming), WebSocket for real-time data
"""
import os, json, csv, io, tempfile, threading, time
from flask import Flask, request, jsonify, Response, send_from_directory, session
from flask_cors import CORS
import requests as req

app = Flask(__name__)
app.config['SECRET_KEY'] = 'petrochemical-ai-integration-2026'
CORS(app, supports_credentials=True)

# 可选的WebSocket支持 - 如果没有安装依赖也能运行
socketio = None
WEBSOCKET_AVAILABLE = False

try:
    from flask_socketio import SocketIO, emit, join_room, leave_room
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
    WEBSOCKET_AVAILABLE = True
    print("[OK] WebSocket support enabled")
except ImportError:
    print("[WARN] flask_socketio not installed, WebSocket functionality unavailable")
    print("       Tip: Run 'pip install Flask-SocketIO python-socketio' to enable WebSocket")

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
DATA_DIR   = os.path.join(BASE_DIR, 'data')
UPLOAD_DIR = os.path.join(BASE_DIR, 'uploads')
CHATS_FILE = os.path.join(DATA_DIR, 'chats.json')

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_EXT = {'.pdf', '.docx', '.csv', '.txt', '.json', '.md', '.py', '.js', '.html', '.css'}

# ==========================================
# 共享状态管理器 - 石化系统与AI系统数据共享
# ==========================================
class SharedState:
    def __init__(self):
        self.lock = threading.Lock()
        self.data = {
            'petrochemical': {
                'status': 'running',
                'personnel': [],
                'equipment': [],
                'sensors': [],
                'alerts': [],
                'selectedZone': None,
                'selectedPerson': None,
                'selectedEquipment': None,
                'lastUpdate': None
            },
            'ai': {
                'connected': False,
                'analysisMode': False,
                'currentQuery': None,
                'suggestions': []
            },
            'integration': {
                'alertsToAI': [],
                'aiCommands': [],
                'biDirectionalSync': True
            }
        }
        self.subscribers = set()
    
    def update_petrochemical(self, data_type, data):
        with self.lock:
            self.data['petrochemical'][data_type] = data
            self.data['petrochemical']['lastUpdate'] = time.time()
    
    def get_petrochemical(self, data_type=None):
        with self.lock:
            if data_type:
                return self.data['petrochemical'].get(data_type)
            return self.data['petrochemical']
    
    def add_alert_for_ai(self, alert):
        with self.lock:
            self.data['integration']['alertsToAI'].append({
                'alert': alert,
                'timestamp': time.time(),
                'processed': False
            })
        # 立即通知AI系统
        if WEBSOCKET_AVAILABLE and socketio:
            socketio.emit('new_alert', alert, room='ai_room')
    
    def add_ai_command(self, command):
        with self.lock:
            self.data['integration']['aiCommands'].append({
                'command': command,
                'timestamp': time.time(),
                'executed': False
            })
        # 立即执行AI命令
        if WEBSOCKET_AVAILABLE and socketio:
            socketio.emit('ai_command', command, room='petrochemical_room')
    
    def get_integration_data(self):
        with self.lock:
            return self.data['integration']

shared_state = SharedState()

# ==========================================
# WebSocket 事件处理 (仅在WebSocket可用时定义)
# ==========================================
if WEBSOCKET_AVAILABLE:
    @socketio.on('connect')
    def handle_connect():
        print(f'Client connected: {request.sid}')
        emit('connected', {'status': 'connected', 'sid': request.sid})

    @socketio.on('disconnect')
    def handle_disconnect():
        print(f'Client disconnected: {request.sid}')

    @socketio.on('join')
    def handle_join(data):
        room = data.get('room', 'default')
        join_room(room)
        print(f'Client {request.sid} joined room: {room}')
        emit('joined', {'room': room, 'status': 'success'})
        
        # 如果是AI系统连接，标记为已连接
        if room == 'ai_room':
            with shared_state.lock:
                shared_state.data['ai']['connected'] = True
            # 发送当前石化系统状态
            emit('petrochemical_state', shared_state.get_petrochemical())
            # 发送待处理的告警
            integration = shared_state.get_integration_data()
            for item in integration['alertsToAI']:
                if not item['processed']:
                    emit('pending_alert', item['alert'])

    @socketio.on('leave')
    def handle_leave(data):
        room = data.get('room', 'default')
        leave_room(room)
        print(f'Client {request.sid} left room: {room}')
        emit('left', {'room': room, 'status': 'success'})
        
        if room == 'ai_room':
            with shared_state.lock:
                shared_state.data['ai']['connected'] = False

    @socketio.on('petrochemical_update')
    def handle_petrochemical_update(data):
        """接收石化系统更新的数据"""
        print(f'Received petrochemical update: {data.get("type")}')
        
        data_type = data.get('type')
        value = data.get('data')
        
        # 更新共享状态
        shared_state.update_petrochemical(data_type, value)
        
        # 广播给AI系统
        emit('petrochemical_update', data, room='ai_room')
        
        # 如果是告警，特殊处理
        if data_type == 'alert':
            shared_state.add_alert_for_ai(value)
        
        emit('update_ack', {'type': data_type, 'status': 'success'})

    @socketio.on('ai_query')
    def handle_ai_query(data):
        """AI系统查询石化数据"""
        print(f'AI query: {data}')
        
        query_type = data.get('query_type')
        response = {'query_type': query_type}
        
        if query_type == 'all':
            response['data'] = shared_state.get_petrochemical()
        elif query_type == 'personnel':
            response['data'] = shared_state.get_petrochemical('personnel')
        elif query_type == 'equipment':
            response['data'] = shared_state.get_petrochemical('equipment')
        elif query_type == 'sensors':
            response['data'] = shared_state.get_petrochemical('sensors')
        elif query_type == 'alerts':
            response['data'] = shared_state.get_petrochemical('alerts')
        elif query_type == 'specific':
            target = data.get('target')
            response['data'] = shared_state.get_petrochemical(target)
        
        emit('ai_query_response', response)

    @socketio.on('ai_command')
    def handle_ai_command(data):
        """AI系统发送控制命令到石化系统"""
        print(f'AI command received: {data}')
        
        command = data.get('command')
        params = data.get('params', {})
        
        # 添加到命令队列
        shared_state.add_ai_command({
            'command': command,
            'params': params,
            'sender': 'ai'
        })
        
        emit('command_ack', {
            'command': command,
            'status': 'queued'
        })

    @socketio.on('ai_analysis_result')
    def handle_ai_analysis(data):
        """AI分析结果返回石化系统"""
        print(f'AI analysis result: {data.get("type")}')
        
        # 广播给石化系统
        emit('ai_analysis', data, room='petrochemical_room')
        
        # 更新AI状态
        with shared_state.lock:
            shared_state.data['ai']['analysisMode'] = data.get('analysisMode', False)
            shared_state.data['ai']['suggestions'] = data.get('suggestions', [])

# ==========================================
# REST API - 状态查询
# ==========================================
@app.route('/api/shared-state')
def get_shared_state():
    """获取共享状态（HTTP轮询备用）"""
    return jsonify(shared_state.get_petrochemical())

@app.route('/api/integration-status')
def get_integration_status():
    """获取集成状态"""
    return jsonify({
        'ai_connected': shared_state.data['ai']['connected'],
        'pending_alerts': len([a for a in shared_state.get_integration_data()['alertsToAI'] if not a['processed']]),
        'pending_commands': len([c for c in shared_state.get_integration_data()['aiCommands'] if not c['executed']])
    })

# ─── Static ───────────────────────────────────────────────
@app.route('/')
@app.route('/index.html')
def index():
    filepath = os.path.join(BASE_DIR, 'index.html')
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/petrochemical.html')
def petrochemical():
    filepath = os.path.join(BASE_DIR, 'petrochemical.html')
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

# ─── Chat Backup / Load ───────────────────────────────────
@app.route('/api/chats', methods=['GET'])
def load_chats():
    if os.path.exists(CHATS_FILE):
        with open(CHATS_FILE, 'r', encoding='utf-8') as f:
            return jsonify(json.load(f))
    return jsonify([])

@app.route('/api/chats', methods=['POST'])
def save_chats():
    data = request.get_json(force=True)
    with open(CHATS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return jsonify({'ok': True, 'count': len(data)})

# ─── File Upload & Text Extraction ────────────────────────
def allowed(filename):
    return os.path.splitext(filename)[1].lower() in ALLOWED_EXT

def extract_text(filepath, ext):
    """Extract plain text from a file based on its extension."""
    if ext == '.pdf':
        import pdfplumber
        text_parts = []
        with pdfplumber.open(filepath) as pdf:
            for i, page in enumerate(pdf.pages):
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(f"[第{i+1}页]\n{page_text}")
                tables = page.extract_tables()
                for table in tables:
                    if table:
                        for row in table:
                            if row:
                                text_parts.append(' | '.join(str(c or '') for c in row))
        result = '\n\n'.join(text_parts)
        if not result.strip():
            return '[PDF文本提取失败：该文件可能是扫描件或图片PDF，无法提取文字内容。请上传可复制文字的PDF文件。]'
        return result

    if ext == '.docx':
        from docx import Document
        doc = Document(filepath)
        return '\n'.join(p.text for p in doc.paragraphs)

    if ext == '.csv':
        rows = []
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            reader = csv.reader(f)
            for i, row in enumerate(reader):
                rows.append(', '.join(row))
                if i >= 500:          # cap at 500 rows
                    rows.append('... (truncated)')
                    break
        return '\n'.join(rows)

    # .txt .json .md .py .js .html .css — read as-is
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        return f.read()

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    file = request.files['file']
    if not file.filename:
        return jsonify({'error': 'Empty filename'}), 400
    if not allowed(file.filename):
        return jsonify({'error': f'Unsupported file type: {file.filename}'}), 400

    ext = os.path.splitext(file.filename)[1].lower()
    tmp = os.path.join(UPLOAD_DIR, file.filename)
    file.save(tmp)

    try:
        content = extract_text(tmp, ext)
        size = os.path.getsize(tmp)
        return jsonify({
            'filename': file.filename,
            'content': content,
            'size': size,
            'type': ext.lstrip('.'),
        })
    except Exception as e:
        return jsonify({'error': f'Failed to parse {file.filename}: {str(e)}'}), 500
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)

# ─── PDF → Images (for multimodal models) ─────────────────
@app.route('/api/pdf-images', methods=['POST'])
def pdf_to_images():
    """Convert PDF pages to base64 images for multimodal models."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    file = request.files['file']
    if not file.filename or not file.filename.lower().endswith('.pdf'):
        return jsonify({'error': 'Not a PDF file'}), 400

    tmp = os.path.join(UPLOAD_DIR, file.filename)
    file.save(tmp)

    try:
        import fitz  # PyMuPDF
        import base64
        doc = fitz.open(tmp)
        total = len(doc)
        images = []
        max_pages = min(total, 10)  # limit to 10 pages

        for i in range(max_pages):
            page = doc[i]
            # Render at 150 DPI (good balance of quality and size)
            mat = fitz.Matrix(150/72, 150/72)
            pix = page.get_pixmap(matrix=mat)
            img_bytes = pix.tobytes('png')
            b64 = base64.b64encode(img_bytes).decode('utf-8')
            images.append({
                'page': i + 1,
                'total': total,
                'data': f'data:image/png;base64,{b64}',
            })

        doc.close()
        return jsonify({
            'filename': file.filename,
            'images': images,
            'total_pages': total,
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Failed to convert PDF: {str(e)}'}), 500
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)

# ─── API Proxy (Streaming SSE) ────────────────────────────
@app.route('/api/proxy', methods=['POST'])
def proxy():
    data = request.get_json(force=True)
    api_url  = data.get('apiUrl', 'https://api.deepseek.com')
    api_key  = data.get('apiKey', '')
    messages = data.get('messages', [])
    model    = data.get('model', 'deepseek-chat')
    temp     = data.get('temperature', 0.7)

    url = f"{api_url.rstrip('/')}/chat/completions"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}',
    }
    body = {
        'model': model,
        'messages': messages,
        'temperature': temp,
        'stream': True,
    }

    try:
        resp = req.post(url, json=body, headers=headers, stream=True, timeout=120)
    except req.exceptions.RequestException as e:
        return jsonify({'error': f'Connection failed: {str(e)}'}), 502

    if resp.status_code != 200:
        err_text = resp.text[:500]
        return jsonify({'error': f'API Error {resp.status_code}: {err_text}'}), resp.status_code

    def generate():
        for chunk in resp.iter_lines():
            if chunk:
                yield chunk.decode('utf-8', errors='replace') + '\n'

    return Response(generate(), content_type='text/event-stream',
                    headers={'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no'})

# ─── Main ─────────────────────────────────────────────────
if __name__ == '__main__':
    print('------------------------------------------------------------')
    print('  DeepSeek Neural Interface - Backend Server')
    print('  Integrated with Petrochemical AI System')
    print('------------------------------------------------------------')
    if WEBSOCKET_AVAILABLE:
        print('  [OK] WebSocket Support: ENABLED')
        print('  [OK] Real-time Data Sync: ENABLED')
        print('  [OK] Bi-directional Communication: ENABLED')
    else:
        print('  [WARN] WebSocket Support: DISABLED')
        print('         Install Flask-SocketIO to enable')
        print('  [OK] Page switching still works')
    print('------------------------------------------------------------')
    print('  Open http://localhost:8080 in your browser')
    print('  Access petrochemical system: http://localhost:8080/petrochemical.html')
    print('------------------------------------------------------------')
    
    if WEBSOCKET_AVAILABLE and socketio:
        socketio.run(app, host='0.0.0.0', port=8080, debug=False, allow_unsafe_werkzeug=True)
    else:
        app.run(host='0.0.0.0', port=8080, debug=False)
