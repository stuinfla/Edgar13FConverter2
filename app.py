from flask import Flask, render_template, request, send_file, flash, redirect, url_for
import os
import shutil
import logging
from logging.handlers import RotatingFileHandler
from xlsx_to_corrected_edgar_xml import create_perfect_edgar_xml as convert_xlsx_to_xml_13f
from finra_6151_converter import perform_6151_conversion
from werkzeug.utils import secure_filename

app = Flask(__name__)

# --- Logging Configuration ---
if not app.debug: 
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info('Application startup')
# --- End Logging Configuration ---

app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB limit

# Load secret key from environment variable or use a default for development
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev_secret_key_۱۲۳')

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
            app.logger.warning('File upload attempt with no file part.')
            return redirect(url_for('index'))
            
        file = request.files['file']
        if file.filename == '':
            flash('No file selected', 'error')
            app.logger.warning('File upload attempt with no file selected.')
            return redirect(url_for('index'))

        conversion_type = request.form.get('conversion_type')
        if not conversion_type:
            flash('Conversion type not specified.', 'error')
            app.logger.warning('Conversion attempt with no conversion type specified.')
            return redirect(url_for('index'))
            
        if file and file.filename.endswith('.xlsx'):
            # Cleanup previous uploads
            cleanup_uploads()
            
            # Save uploaded file
            original_filename_secure = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], original_filename_secure)
            file.save(filepath)
            app.logger.info(f"File '{original_filename_secure}' uploaded successfully.")
            
            output_xml_filename = None
            xml_is_valid = None 
            xml_validation_errors = [] 
            
            try:
                if conversion_type == '13F':
                    output_xml_filename = original_filename_secure.lower().replace('.xlsx', '.xml')
                    output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_xml_filename)
                    app.logger.info(f"Starting 13F conversion for '{original_filename_secure}' to '{output_xml_filename}'.")
                    convert_xlsx_to_xml_13f(filepath, output_path)
                    flash(f'Successfully converted (13F) {original_filename_secure} to {output_xml_filename}', 'success')
                    app.logger.info(f"13F conversion successful for '{original_filename_secure}'. Output: {output_xml_filename}")
                
                elif conversion_type == '6151':
                    firm_name = request.form.get('firm_name')
                    year = request.form.get('year')
                    qtr = request.form.get('qtr')

                    if not all([firm_name, year, qtr]):
                        flash('Firm Name, Year, and Quarter are required for 6151 conversion.', 'error')
                        app.logger.warning(f"Missing parameters for 6151 conversion of '{original_filename_secure}'. Firm: {firm_name}, Year: {year}, Qtr: {qtr}")
                        return redirect(url_for('index'))
                    
                    app.logger.info(f"Starting 6151 conversion for '{original_filename_secure}'. Firm: {firm_name}, Year: {year}, Qtr: {qtr}")
                    generated_xml_full_path, xml_is_valid, xml_validation_errors = perform_6151_conversion(
                        excel_filepath=filepath, 
                        output_dir=app.config['UPLOAD_FOLDER'], 
                        firm_name=firm_name, 
                        year=year, 
                        qtr=qtr
                    )

                    if generated_xml_full_path:
                        output_xml_filename = os.path.basename(generated_xml_full_path)
                        app.logger.info(f"6151 conversion for '{original_filename_secure}' produced '{output_xml_filename}'. Validation status: {'VALID' if xml_is_valid else 'INVALID'}")
                        if xml_is_valid:
                            flash(f'Successfully converted (6151) {original_filename_secure} to {output_xml_filename}. XML is valid.', 'success')
                        else:
                            error_summary = "; ".join(xml_validation_errors[:3]) 
                            flash(f'Converted (6151) {original_filename_secure} to {output_xml_filename}, but XML validation failed: {error_summary}', 'warning')
                            app.logger.warning(f"XML validation failed for '{output_xml_filename}'. Errors: {xml_validation_errors}")
                    else:
                        error_summary = "; ".join(xml_validation_errors[:3]) if xml_validation_errors else "Unknown error during XML creation."
                        flash(f'Failed to convert (6151) {original_filename_secure}: {error_summary}', 'error')
                        app.logger.error(f"6151 XML creation failed for '{original_filename_secure}'. Errors: {xml_validation_errors}")
                        return redirect(url_for('index')) 
                
                else:
                    flash('Invalid conversion type selected.', 'error')
                    app.logger.error(f"Invalid conversion type '{conversion_type}' selected for file '{original_filename_secure}'.")
                    return redirect(url_for('index'))

                return render_template('index.html', 
                                     converted_file=output_xml_filename,
                                     original_filename=original_filename_secure,
                                     conversion_type_processed=conversion_type,
                                     xml_is_valid=xml_is_valid, 
                                     xml_validation_errors=xml_validation_errors) 
            
            except Exception as e:
                flash(f'Conversion error for {conversion_type}: {str(e)}', 'error')
                app.logger.error(f"Conversion error for {conversion_type} on file {original_filename_secure}: {str(e)}", exc_info=True)
                return redirect(url_for('index'))
                
        flash('Invalid file type. Please upload a .xlsx file.', 'error')
        app.logger.warning(f"Invalid file type uploaded: '{file.filename if file else 'N/A'}'.")
        return redirect(url_for('index'))
        
    except Exception as e:
        flash(f'An unexpected error occurred: {str(e)}', 'error')
        app.logger.error(f"An unexpected error occurred in /convert route: {str(e)}", exc_info=True)
        return redirect(url_for('index'))

@app.route('/download/<filename>')
def download_file(filename):
    try:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if not os.path.exists(file_path):
            flash('File not found', 'error')
            app.logger.error(f"Download attempt for non-existent file: {filename}")
            return redirect(url_for('index'))
        app.logger.info(f"'{filename}' downloaded successfully.")
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        flash(f'Download error: {str(e)}', 'error')
        app.logger.error(f"Error during download of file '{filename}': {str(e)}", exc_info=True)
        return redirect(url_for('index'))

if __name__ == '__main__':
    is_debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    if is_debug_mode:
        app.logger.info('Application starting in DEBUG mode.')
    else:
        app.logger.info('Application starting in PRODUCTION mode (Debug=False).') 

    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=is_debug_mode)
