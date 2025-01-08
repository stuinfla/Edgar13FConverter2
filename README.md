# EDGAR Form 13F XML Converter

This application converts Excel files containing stock position data into properly formatted XML files compliant with the SEC's EDGAR Form 13F filing requirements.

## Repository
https://github.com/stuinfla/Edgar13FConverter2

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
   git clone https://github.com/stuinfla/Edgar13FConverter2.git
   cd Edgar13FConverter2
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run locally:
   ```bash
   gunicorn app:app
   ```
   Access the application at http://localhost:5000

## Usage
1. Prepare your Excel file following the required format
2. Access the web interface at http://localhost:5000
3. Upload your .xlsx file
4. Download the generated XML file

## Compliance
The application strictly follows:
- EDGAR Form 13F XML Technical Specification (v1.0)
- eis_13FDocument.xsd schema
- SEC filing requirements for institutional investment managers

## Deployment
This application uses GitHub-based deployment to Railway. The deployment process is:

1. Connect your GitHub repository to Railway:
   - Go to Railway dashboard
   - Create new project
   - Select "Deploy from GitHub repo"
   - Choose this repository

2. Configure environment variables through Railway dashboard:
   - Set required environment variables
   - Configure production settings

3. Automatic deployments:
   - All changes pushed to main branch will automatically deploy
   - No manual deployment is allowed
   - Deployment status can be monitored in Railway dashboard

4. Access the deployed application at:
   https://edgar13fconverter2-production.up.railway.app

## Testing
Sample input/output files are provided:
- Input/Zeno 13F 1Q '24.xlsx
- Output/Zeno_13F_1Q_24.xml
- Output/zeno1q2413f.xml

## Documentation
- Conversion specs/EDGAR Form 13F XML Technical Specification.pdf
- Conversion specs/eis_13FDocument.xsd
- README.md (this file)
