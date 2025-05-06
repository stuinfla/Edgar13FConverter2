# EDGAR Form 13F & FINRA Rule 6151 XML Converter - Version 2.5

## Project Purpose
This application was developed to streamline the process of converting Excel-based financial data into SEC-compliant EDGAR XML format for Form 13F filings and FINRA-compliant XML for Rule 6151 (Held Order Routing Reports). The goal is to provide institutional investment managers and broker-dealers with a reliable, automated solution that ensures compliance with regulatory requirements while reducing manual effort and potential errors.

## Version 1.2 Highlights
- **Dual Conversion Capability:** Supports both EDGAR Form 13F and FINRA Rule 6151 XML conversions.
- **FINRA Rule 6151 Support:**
    - Converts Excel data for Held Order Routing Reports to compliant XML.
    - Validates generated 6151 XML against the official FINRA `oh-20191231.xsd` schema.
    - User interface for selecting conversion type and providing 6151-specific inputs (Firm Name, Year, Quarter).
    - Displays XML validation status (Verified/Failed with errors) directly in the UI for 6151 reports.
- Stable Excel to EDGAR XML conversion functionality (from v1.1).
- Enhanced robustness in handling diverse Excel column names and structures for 13F (from v1.1).
- Improved error reporting for missing data.
- Proper deployment configuration for Railway.
- Complete documentation and sample files.
- Production-ready codebase.
- Automatic cleanup of temporary files.
- Copyright notice added to the user interface.

## Version 2.5 Highlights
- **UI Enhancements:**
    - Added tooltips with info icons for key input fields for better user guidance.
    - Implemented a "Clear Form" button to easily reset all inputs.
    - Dynamically updating copyright year.
    - Version number (v2.5) displayed in the UI.
- **Bug Fixes:**
    - Corrected duplicated copyright notice.

## Key Features

### General
- Web interface for easy file upload and conversion type selection.
- Automatic cleanup of temporary uploaded files.

### EDGAR Form 13F Conversion
- Converts .xlsx files to EDGAR-compliant XML for Form 13F.
- Validates against the official EDGAR Form 13F XML Technical Specification.
- Uses the `eis_13FDocument.xsd` schema for validation.
- **Flexible Column Name Recognition:** Intelligently searches for required data columns using primary names and common synonyms (case-insensitive).
- **Positional Fallback:** For critical 13F data, can fall back to predefined positional column names if headers are not found.
- **Graceful Handling of Missing "None" Voting Data:** Defaults to `0` if the "None" voting authority column is missing.
- **Clearer Error Messaging:** Detailed error messages for missing essential 13F columns.

### FINRA Rule 6151 Conversion (New in v1.2)
- Converts .xlsx files (formatted for 6151) to FINRA Rule 6151 compliant XML for Held Order Routing Reports.
- Validates generated XML against the official FINRA `oh-20191231.xsd` schema.
- Accepts Firm Name, Reporting Year, and Reporting Quarter as inputs for 6151 reports.
- Displays XML validation status (Verified/Failed with errors) in the user interface post-conversion.

## Development History
This project was developed through an iterative process:
1. Initial prototype development for 13F.
2. Extensive testing with sample 13F data.
3. Compliance verification with SEC specifications for 13F.
4. Deployment configuration and optimization.
5. Version 1.0 release and testing (13F).
6. Version 1.1 stabilization and production deployment (13F robustness enhancements).
7. Version 1.2 addition of FINRA Rule 6151 conversion and validation functionality.

## Repository
https://github.com/stuinfla/Edgar13FConverter2

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/stuinfla/Edgar13FConverter2.git
   cd Edgar13FConverter2
   ```

2. Create and activate a virtual environment (recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run locally:
   ```bash
   python3 app.py
   ```
   The application will typically be accessible at http://localhost:8080 or http://127.0.0.1:8080.

## Usage
1. Prepare your Excel file following the required format for either 13F or 6151.
2. Access the web interface (e.g., http://localhost:8080).
3. Select the desired `Conversion Type` (EDGAR Form 13F or FINRA Rule 6151).
4. If FINRA Rule 6151 is selected, provide the `Firm Name`, `Reporting Year`, and `Reporting Quarter`.
5. Upload your .xlsx file.
6. Click the "Convert to ... XML" button.
7. The application will display a success message, the names of the original and converted files, and (for 6151) the XML validation status.
8. Download the generated XML file.

## Compliance

### EDGAR Form 13F
The application strictly follows:
- EDGAR Form 13F XML Technical Specification (v1.0)
- `eis_13FDocument.xsd` schema
- SEC filing requirements for institutional investment managers

### FINRA Rule 6151 (New in v1.2)
- FINRA Rule 6151 for Held NMS Stocks and Listed Options Order Routing Public Disclosure.
- FINRA Order Handling Data Technical Specification (`oh-20191231.xsd` schema).

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
Sample input and output files are provided to demonstrate functionality and expected formats.

### EDGAR Form 13F Examples:
- **Primary Example:**
    - Input:  `Test Input files 13F/zenocapital1q25positions-1.xlsx`
    - Output: `Test output files 13F/zenocapital1q25positions-1.xml`
- *Additional 13F examples can be found in the `Input/`, `Test Input files 13F/`, `Output/`, `Sample outputs/`, and `Test output files 13F/` directories.*

### FINRA Rule 6151 Examples:
- **Primary Example:**
    - Input:  `Test file Finra 6151/281065_606_NMS_2024_Q2.xlsx`
    - Output: `Test file Finra 6151/281065_606_NMS_2024_Q2.xml`
- *Additional 6151 examples (input .xlsx and corresponding .xml output) can be found in the `Test file Finra 6151/` directory.*

## Documentation
Key technical specifications and schemas are stored in the repository:

### EDGAR Form 13F:
- `Conversion specs/EDGAR Form 13F XML Technical Specification.pdf`
- `Conversion specs/eis_13FDocument.xsd`
- `Conversion specs/eis_Common.xsd`

### FINRA Rule 6151:
- `Finra 6151 requirements/Order_Handling_Data_Technical_Specification_20190331.pdf`
- `Finra 6151 requirements/oh-20191231.xsd`
- Other supporting documents in `Finra 6151 requirements/`

Additional documentation:
- README.md (this file)
- Sample input/output files in their respective test directories.

---
*Copyright 2025 ISO Vision LLC.*
