import os
import sys

# Add the project root to the Python path to allow importing xlsx_to_corrected_edgar_xml
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

try:
    from xlsx_to_corrected_edgar_xml import create_perfect_edgar_xml
except ImportError as e:
    print(f"Error: Could not import 'create_perfect_edgar_xml' from 'xlsx_to_corrected_edgar_xml.py'.")
    print(f"Please ensure 'xlsx_to_corrected_edgar_xml.py' is in the same directory as this script or in the Python path.")
    print(f"Details: {e}")
    sys.exit(1)

def run_batch_conversions():
    """Runs the Excel to XML conversion for predefined test files."""
    base_dir = project_root
    
    input_dir = os.path.join(base_dir, "Test Input files 13F")
    output_dir_base = os.path.join(base_dir, "Test output files 13F")

    # Ensure the base output directory exists
    os.makedirs(output_dir_base, exist_ok=True)

    test_files = [
        "zenocapital1q25positions-1.xlsx",
        "zenocapital4q2413fpositions.xlsx"
    ]

    print(f"Base directory: {base_dir}")
    print(f"Input directory: {input_dir}")
    print(f"Output directory: {output_dir_base}")

    for excel_filename in test_files:
        input_excel_path = os.path.join(input_dir, excel_filename)
        
        # Output filename will keep original case, just change extension
        xml_filename = os.path.splitext(excel_filename)[0] + ".xml"
        output_xml_path = os.path.join(output_dir_base, xml_filename)

        print(f"\nProcessing: {input_excel_path}")
        print(f"Outputting to: {output_xml_path}")

        if not os.path.exists(input_excel_path):
            print(f"Error: Input file not found: {input_excel_path}")
            continue

        try:
            create_perfect_edgar_xml(input_excel_path, output_xml_path)
            print(f"Successfully converted '{excel_filename}' to '{xml_filename}'")
        except Exception as e:
            print(f"Error converting '{excel_filename}': {e}")
            import traceback
            traceback.print_exc() # Print full traceback for debugging

if __name__ == "__main__":
    run_batch_conversions()
