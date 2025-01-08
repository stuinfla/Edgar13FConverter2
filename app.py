from flask import Flask, render_template, request, send_file, flash, redirect, url_for
import os
import shutil
from xlsx_to_corrected_edgar_xml import create_perfect_edgar_xml as convert_xlsx_to_xml
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB limit
app.secret_key = 'your-secret-key-here'  # Change this to a real secret key in production

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def cleanup_uploads():
    """Remove all files from uploads directory"""
    if os.path.exists(app.config['UPLOAD_FOLDER']):
        shutil.rmtree(app.config['UPLOAD_FOLDER'])
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    try:
        if 'file' not in request.files:
            flash('No file uploaded', 'error')
            return redirect(url_for('index'))
            
        file = request.files['file']
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(url_for('index'))
            
        if file and file.filename.endswith('.xlsx'):
            # Cleanup previous uploads
            cleanup_uploads()
            
            # Save uploaded file
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Convert to XML
            output_filename = filename.replace('.xlsx', '.xml')
            output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
            
            try:
                convert_xlsx_to_xml(filepath, output_path)
                original_filename = secure_filename(file.filename)
                flash(f'Successfully converted {original_filename} to {output_filename}', 'success')
                return render_template('index.html', 
                                    converted_file=output_filename,
                                    original_filename=original_filename)
            except Exception as e:
                flash(f'Conversion error: {str(e)}', 'error')
                return redirect(url_for('index'))
                
        flash('Invalid file type. Please upload a .xlsx file.', 'error')
        return redirect(url_for('index'))
        
    except Exception as e:
        flash(f'An unexpected error occurred: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/download/<filename>')
def download_file(filename):
    try:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if not os.path.exists(file_path):
            flash('File not found', 'error')
            return redirect(url_for('index'))
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        flash(f'Download error: {str(e)}', 'error')
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
