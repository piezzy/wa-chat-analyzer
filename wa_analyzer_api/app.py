from flask import Flask, request, jsonify
from preprocess import preprocess
from stats import fetch_stats
import re
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'chat' not in request.files:
        return jsonify({'error': 'No file part'}), 400
        
    file = request.files['chat']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400

    try:
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        with open(filepath, 'r', encoding='utf-8') as f:
            data = f.read()

        selected_user = request.form.get('user', 'Overall')

        df = preprocess(data)
        num_messages, num_words, media_count, links = fetch_stats(selected_user, df)

        os.remove(filepath)

        result = {
            'status': 'success',
            'user': selected_user,
            'num_messages': num_messages,
            'num_words': num_words,
            'media_count': media_count,
            'links': links
        }
        
        return jsonify(result)
        
    except Exception as e:
        if 'filepath' in locals() and os.path.exists(filepath):
            os.remove(filepath)
            
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)