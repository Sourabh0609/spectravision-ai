from flask import Flask, render_template, request, send_file, jsonify, url_for
import os
from pathlib import Path
import uuid
from werkzeug.utils import secure_filename
from colorize import Colorizer
from bg_remove import remove_background
from style_transfer import apply_style_transfer
from video_colorize import colorize_video

ROOT_DIR = Path(__file__).parent

app = Flask(__name__, 
            template_folder=str(ROOT_DIR / 'templates'),
            static_folder=str(ROOT_DIR / 'static'))

app.config['UPLOAD_FOLDER'] = str(ROOT_DIR / 'static' / 'uploads')
app.config['RESULT_FOLDER'] = str(ROOT_DIR / 'static' / 'results')
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size

ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'webp'}
ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'webm'}

# Initialize colorizer
colorizer = None

def allowed_file(filename, file_type='image'):
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    if file_type == 'image':
        return ext in ALLOWED_IMAGE_EXTENSIONS
    elif file_type == 'video':
        return ext in ALLOWED_VIDEO_EXTENSIONS
    return ext in ALLOWED_IMAGE_EXTENSIONS or ext in ALLOWED_VIDEO_EXTENSIONS

def get_colorizer():
    global colorizer
    if colorizer is None:
        colorizer = Colorizer()
    return colorizer

def is_video_file(filename):
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in ALLOWED_VIDEO_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    filter_type = request.form.get('filter', 'bw_to_color')
    style_option = request.form.get('style', 'pencil')
    media_type = request.form.get('media_type', 'image')
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Determine if it's a video or image
    is_video = is_video_file(file.filename)
    
    if not allowed_file(file.filename, 'video' if is_video else 'image'):
        return jsonify({'error': 'Invalid file type'}), 400
    
    # Generate unique filename
    file_ext = file.filename.rsplit('.', 1)[1].lower()
    unique_id = str(uuid.uuid4())
    input_filename = f"{unique_id}_input.{file_ext}"
    
    # For background removal or video, use appropriate extension
    if filter_type == 'bg_removal':
        output_filename = f"{unique_id}_output.png"
    elif is_video:
        output_filename = f"{unique_id}_output.mp4"
    else:
        output_filename = f"{unique_id}_output.{file_ext}"
    
    input_path = os.path.join(app.config['UPLOAD_FOLDER'], input_filename)
    output_path = os.path.join(app.config['RESULT_FOLDER'], output_filename)
    
    # Save uploaded file
    file.save(input_path)
    
    try:
        # Process based on media type and filter
        if is_video:
            # Video processing
            if filter_type == 'bw_to_color':
                colorize_video(input_path, output_path)
            else:
                return jsonify({'error': 'Only B&W to Color is supported for videos currently'}), 400
        else:
    # Image processing
            if filter_type == 'bw_to_color':
                # This should ONLY be called for B&W images
                # For color images, this will produce weird results
                colorizer_instance = get_colorizer()
                colorizer_instance.colorize(input_path, output_path)
    
            elif filter_type == 'style_transfer':
                # This works on B&W AND Color images
                apply_style_transfer(input_path, output_path, style=style_option)
    
            elif filter_type == 'bg_removal':
            # This works on B&W AND Color images
                 remove_background(input_path, output_path)
            else:
                return jsonify({'error': 'Invalid filter type'}), 400
        
        return jsonify({
            'success': True,
            'input_url': f'/static/uploads/{input_filename}',
            'output_url': f'/static/results/{output_filename}',
            'filter': filter_type,
            'media_type': 'video' if is_video else 'image'
        })
    
    except Exception as e:
        return jsonify({'error': f'Processing failed: {str(e)}'}), 500

@app.route('/download/<filename>')
def download(filename):
    file_path = os.path.join(app.config['RESULT_FOLDER'], filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return jsonify({'error': 'File not found'}), 404

if __name__ == '__main__':
    # Ensure folders exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['RESULT_FOLDER'], exist_ok=True)
    
    app.run(host='0.0.0.0', port=3000, debug=False)