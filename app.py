from flask import Flask, render_template, request, send_file, flash, redirect, url_for
import os
import shutil
from xlsx_to_corrected_edgar_xml import create_perfect_edgar_xml as convert_xlsx_to_xml_13f
from finra_6151_converter import perform_6151_conversion
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

        conversion_type = request.form.get('conversion_type')
        if not conversion_type:
            flash('Conversion type not specified.', 'error')
            return redirect(url_for('index'))
            
        if file and file.filename.endswith('.xlsx'):
            # Cleanup previous uploads
            cleanup_uploads()
            
            # Save uploaded file
            original_filename_secure = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], original_filename_secure)
            file.save(filepath)
            
            output_xml_filename = None
            xml_is_valid = None # For 6151 validation status
            xml_validation_errors = [] # For 6151 validation errors
            
            try:
                if conversion_type == '13F':
                    output_xml_filename = original_filename_secure.lower().replace('.xlsx', '.xml')
                    output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_xml_filename)
                    convert_xlsx_to_xml_13f(filepath, output_path)
                    flash(f'Successfully converted (13F) {original_filename_secure} to {output_xml_filename}', 'success')
                
                elif conversion_type == '6151':
                    firm_name = request.form.get('firm_name')
                    year = request.form.get('year')
                    qtr = request.form.get('qtr')

                    if not all([firm_name, year, qtr]):
                        flash('Firm Name, Year, and Quarter are required for 6151 conversion.', 'error')
                        return redirect(url_for('index'))
                    
                    generated_xml_full_path, xml_is_valid, xml_validation_errors = perform_6151_conversion(
                        excel_filepath=filepath, 
                        output_dir=app.config['UPLOAD_FOLDER'], 
                        firm_name=firm_name, 
                        year=year, 
                        qtr=qtr
                    )

                    if generated_xml_full_path:
                        output_xml_filename = os.path.basename(generated_xml_full_path)
                        if xml_is_valid:
                            flash(f'Successfully converted (6151) {original_filename_secure} to {output_xml_filename}. XML is valid.', 'success')
                        else:
                            error_summary = "; ".join(xml_validation_errors[:3]) # Show first 3 errors
                            flash(f'Converted (6151) {original_filename_secure} to {output_xml_filename}, but XML validation failed: {error_summary}', 'warning')
                    else:
                        # XML creation itself failed
                        error_summary = "; ".join(xml_validation_errors[:3]) if xml_validation_errors else "Unknown error during XML creation."
                        flash(f'Failed to convert (6151) {original_filename_secure}: {error_summary}', 'error')
                        return redirect(url_for('index')) # Redirect if file creation failed
                
                else:
                    flash('Invalid conversion type selected.', 'error')
                    return redirect(url_for('index'))

                return render_template('index.html', 
                                     converted_file=output_xml_filename,
                                     original_filename=original_filename_secure,
                                     conversion_type_processed=conversion_type,
                                     xml_is_valid=xml_is_valid, # Pass validation status to template
                                     xml_validation_errors=xml_validation_errors) # Pass errors to template
            
            except Exception as e:
                flash(f'Conversion error for {conversion_type}: {str(e)}', 'error')
                # Log the full error for debugging
                app.logger.error(f"Conversion error for {conversion_type} on file {original_filename_secure}: {e}", exc_info=True)
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
    port = int(os.environ.get('PORT', 8080)) # Changed default to 8080
    app.run(host='0.0.0.0', port=port)
