# EDGAR Form 13F XML Converter - Version 1.1 (Stable Release)

## Project Purpose
This application was developed to streamline the process of converting Excel-based stock position data into SEC-compliant EDGAR XML format for Form 13F filings. The goal is to provide institutional investment managers with a reliable, automated solution that ensures compliance with SEC regulations while reducing manual effort and potential errors.

## Version 1.1 Highlights
- Stable Excel to EDGAR XML conversion functionality
- Enhanced robustness in handling diverse Excel column names and structures
- Improved error reporting for missing data
- Proper deployment configuration for Railway
- Complete documentation and sample files
- Production-ready codebase
- Automatic cleanup of temporary files

## Key Features
- Converts .xlsx files to EDGAR-compliant XML
- Validates against the official EDGAR Form 13F XML Technical Specification
- Uses the eis_13FDocument.xsd schema for validation
- Web interface for easy file upload and conversion
- Automatic cleanup of temporary files

### Enhanced Robustness (May 2025 Updates)
To address real-world variations in client Excel files, the converter has been significantly upgraded for flexibility:
- **Flexible Column Name Recognition:** The application now intelligently searches for required data columns using not only their primary expected names (e.g., "Shares/Principal") but also a configurable list of common synonyms (e.g., "Shrs/Prn Typ", "Type"). This matching is case-insensitive.
- **Positional Fallback for Critical Data:** For essential fields like "Shares/Principal", "Investment Discretion", and voting authorities ("Sole", "Shared", "None"), if no matching header is found (even after checking synonyms), the system can fall back to using predefined positional column names (e.g., "Unnamed: 5", "Unnamed: 6") if such columns exist in the input file.
- **Graceful Handling of Missing "None" Voting Data:** The "None" voting authority column is now treated as optional. If this column (or its equivalent) is not found in the Excel file, its value will default to `0` for all securities in the generated XML, allowing the conversion to proceed without error.
- **Clearer Error Messaging:** If essential required columns are still missing after all checks, the application now provides a detailed error message listing exactly which columns (and their expected synonyms/fallbacks) could not be located.

## Development History
This project was developed through an iterative process:
1. Initial prototype development
2. Extensive testing with sample data
3. Compliance verification with SEC specifications
4. Deployment configuration and optimization
5. Version 1.0 release and testing
6. Version 1.1 stabilization and production deployment

## Repository
https://github.com/stuinfla/Edgar13FConverter2

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

5. Monitor deployment status:
   - Railway dashboard: https://railway.com/project/1276b3a3-c08e-41cc-9744-b64ca1abd7a8/service/e3f7c381-d089-47b3-9f6e-8b08532e06ac?environmentId=b80de425-ea66-4c46-b813-56ec84a45159
   - Verify deployment status is "Successful"
   - Check logs for any errors
   - Confirm service status is "Running"

## Testing
Sample input/output files are provided:
- Input/Zeno 13F 1Q '24.xlsx
- Output/Zeno_13F_1Q_24.xml
- Output/zeno1q2413f.xml

## Documentation
The complete technical specifications for the application are permanently stored in the Conversion Specs folder:
- Conversion specs/EDGAR Form 13F XML Technical Specification.pdf
- Conversion specs/eis_13FDocument.xsd

Additional documentation:
- README.md (this file)
- Sample input/output files in Input/ and Output/ folders
