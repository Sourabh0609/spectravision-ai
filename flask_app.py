
from flask import Flask, render_template, request, send_file, jsonify
import os
from pathlib import Path
import uuid

from colorize import Colorizer
from bg_remove import remove_background
from style_transfer import apply_style_transfer

ROOT_DIR = Path(__file__).parent

app = Flask(
    __name__,
    template_folder=str(ROOT_DIR / 'templates'),
    static_folder=str(ROOT_DIR / 'static')
)

app.config['UPLOAD_FOLDER'] = str(ROOT_DIR / 'static' / 'uploads')
app.config['RESULT_FOLDER'] = str(ROOT_DIR / 'static' / 'results')
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

# Ensure folders exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['RESULT_FOLDER'], exist_ok=True)

ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'webp'}

colorizer = None


def allowed_file(filename):
    if '.' not in filename:
        return False

    ext = filename.rsplit('.', 1)[1].lower()
    return ext in ALLOWED_IMAGE_EXTENSIONS


def get_colorizer():
    global colorizer

    if colorizer is None:
        colorizer = Colorizer()

    return colorizer


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

    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid image type'}), 400

    file_ext = file.filename.rsplit('.', 1)[1].lower()

    unique_id = str(uuid.uuid4())

    input_filename = f"{unique_id}_input.{file_ext}"

    if filter_type == 'bg_removal':
        output_filename = f"{unique_id}_output.png"
    else:
        output_filename = f"{unique_id}_output.{file_ext}"

    input_path = os.path.join(app.config['UPLOAD_FOLDER'], input_filename)
    output_path = os.path.join(app.config['RESULT_FOLDER'], output_filename)

    file.save(input_path)

    try:

        if filter_type == 'bw_to_color':

            colorizer_instance = get_colorizer()
            colorizer_instance.colorize(input_path, output_path)

        elif filter_type == 'style_transfer':

            apply_style_transfer(
                input_path,
                output_path,
                style=style_option
            )

        elif filter_type == 'bg_removal':

            remove_background(input_path, output_path)

        else:
            return jsonify({'error': 'Invalid filter type'}), 400

        return jsonify({
            'success': True,
            'input_url': f'/static/uploads/{input_filename}',
            'output_url': f'/static/results/{output_filename}'
        })

    except Exception as e:

        return jsonify({
            'error': f'Processing failed: {str(e)}'
        }), 500


@app.route('/download/<filename>')
def download(filename):

    file_path = os.path.join(
        app.config['RESULT_FOLDER'],
        filename
    )

    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)

    return jsonify({'error': 'File not found'}), 404


if __name__ == '__main__':

    port = int(os.environ.get("PORT", 10000))

    app.run(
        host='0.0.0.0',
        port=port,
        debug=False
    )

