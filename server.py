"""
DeepSeek Neural Interface — Flask Backend
Handles: chat backup/load, file upload/parsing, API proxy (streaming)
"""
import os, json, csv, io, tempfile
from flask import Flask, request, jsonify, Response, send_from_directory
from flask_cors import CORS
import requests as req

app = Flask(__name__)
CORS(app)

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
DATA_DIR   = os.path.join(BASE_DIR, 'data')
UPLOAD_DIR = os.path.join(BASE_DIR, 'uploads')
CHATS_FILE = os.path.join(DATA_DIR, 'chats.json')

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_EXT = {'.pdf', '.docx', '.csv', '.txt', '.json', '.md', '.py', '.js', '.html', '.css'}

# ─── Static ───────────────────────────────────────────────
@app.route('/')
def index():
    return send_from_directory(BASE_DIR, 'index.html')

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
    print('=' * 50)
    print('  DeepSeek Neural Interface — Backend Server')
    print('  Open http://localhost:8080 in your browser')
    print('=' * 50)
    app.run(host='0.0.0.0', port=8080, debug=False)
