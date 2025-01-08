# EDGAR Form 13F XML Converter

This application converts Excel files containing stock position data into properly formatted XML files compliant with the SEC's EDGAR Form 13F filing requirements.

## Key Features
- Converts .xlsx files to EDGAR-compliant XML
- Validates against the official EDGAR Form 13F XML Technical Specification
- Uses the eis_13FDocument.xsd schema for validation
- Web interface for easy file upload and conversion
- Automatic cleanup of temporary files

## Requirements
- Python 3.9+
- Required packages (see requirements.txt)
- Railway account for deployment

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/[your-repo].git
   cd edgar-13f-converter
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run locally:
   ```bash
   gunicorn app:app
   ```

## Usage
1. Access the web interface at http://localhost:5000
2. Upload a .xlsx file following the required format
3. Download the generated XML file

## Compliance
The application strictly follows:
- EDGAR Form 13F XML Technical Specification (v1.0)
- eis_13FDocument.xsd schema
- SEC filing requirements for institutional investment managers

## Deployment
1. Push to GitHub repository
2. Connect repository to Railway
3. Configure environment variables:
   - SECRET_KEY
   - PORT
4. Deploy through Railway dashboard

## Testing
Sample input/output files are provided in the Sample outputs/ directory:
- Zeno 13F 1Q '24.xlsx (input)
- Zeno_13F_1Q_24.xml (output)
- zeno1q2413f.xml (output)

## Documentation
- Conversion specs/EDGAR Form 13F XML Technical Specification.pdf
- Conversion specs/eis_13FDocument.xsd
