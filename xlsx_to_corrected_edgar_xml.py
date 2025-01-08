import pandas as pd
from xml.etree.ElementTree import Element, SubElement, ElementTree, tostring
import os
import glob
import xml.dom.minidom as minidom
import re

def create_perfect_edgar_xml(input_xlsx, output_xml):
    # Read the Excel file
    df = pd.read_excel(input_xlsx)
    
    # Create the root element with proper namespace declaration and prefix
    root = Element("ns1:informationTable", attrib={
        "xmlns:ns1": "http://www.sec.gov/edgar/document/thirteenf/informationtable",
        "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance"
    })

    # Iterate through each row in the dataframe
    for _, row in df.iterrows():
        # Create an infoTable entry with namespace prefix
        info_table = SubElement(root, "ns1:infoTable")
        
        # Required fields with namespace prefix
        SubElement(info_table, "ns1:nameOfIssuer").text = str(row["Name of Issuer"]).strip()
        SubElement(info_table, "ns1:titleOfClass").text = str(row["Title of Class"]).strip()
        SubElement(info_table, "ns1:cusip").text = str(row["Cusip"]).strip()
        
        # Optional FIGI field with namespace prefix
        if pd.notnull(row.get("FIGI", None)):
            SubElement(info_table, "ns1:figi").text = str(row["FIGI"]).strip()
        
        # Value rounded to nearest dollar with namespace prefix
        value = round(float(row["Value (to the nearest dollar)"]))
        SubElement(info_table, "ns1:value").text = str(int(value)).strip()
        
        # Shares or principal amount with namespace prefix
        shrs_or_prn_amt = SubElement(info_table, "ns1:shrsOrPrnAmt")
        SubElement(shrs_or_prn_amt, "ns1:sshPrnamt").text = str(int(row["Shares or Principal Amount"])).strip()
        SubElement(shrs_or_prn_amt, "ns1:sshPrnamtType").text = str(row["Shares/Principal"]).strip()
        
        # Optional put/call field with namespace prefix
        if pd.notnull(row.get("put/call", None)):
            SubElement(info_table, "ns1:putCall").text = str(row["put/call"]).strip()
        
        # Required investment discretion with namespace prefix
        SubElement(info_table, "ns1:investmentDiscretion").text = str(row["Investment Discretion"]).strip()
        
        # Optional other manager field with namespace prefix
        if pd.notnull(row.get("Other Managers", None)):
            SubElement(info_table, "ns1:otherManager").text = str(int(row["Other Managers"])).strip()
        
        # Voting authority with namespace prefix
        voting_authority = SubElement(info_table, "ns1:votingAuthority")
        SubElement(voting_authority, "ns1:Sole").text = str(int(row["Sole"])).strip()
        SubElement(voting_authority, "ns1:Shared").text = str(int(row["Shared"])).strip()
        SubElement(voting_authority, "ns1:None").text = str(int(row["None"])).strip()
    
    # Convert the XML tree to a string with proper indentation
    raw_xml = tostring(root, encoding="utf-8", method="xml")
    pretty_xml = minidom.parseString(raw_xml).toprettyxml(indent="	", encoding="utf-8")
    
    # Write the XML to file with standalone="yes" in the declaration
    with open(output_xml, "wb") as file:
        file.write(b'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n')
        # Remove any duplicate XML declarations from pretty_xml
        pretty_xml = pretty_xml.replace(b'<?xml version="1.0" encoding="utf-8"?>\n', b'')
        file.write(pretty_xml.strip())
    print(f"Perfect EDGAR-compliant XML file created: {output_xml}")

def generate_output_filename(input_filename):
    """Generate output filename in SEC-compliant format"""
    # Convert input filename to lowercase immediately
    input_filename = input_filename.lower()
    
    # Extract base name without extension
    base_name = os.path.splitext(input_filename)[0]
    
    # Remove special characters and spaces
    clean_name = re.sub(r"[^a-z0-9]", "", base_name)
    
    # Ensure the filename ends with '13f'
    if not clean_name.endswith("13f"):
        clean_name += "13f"
    
    # Add quarter and year if not present
    if not re.search(r"q\d{2}", clean_name):
        # Get current quarter and year
        today = pd.Timestamp.today()
        quarter = (today.month - 1) // 3 + 1
        year = today.year % 100
        clean_name += f"q{quarter}{year:02d}"
    
    # Ensure final filename is lowercase
    output_filename = f"{clean_name}.xml".lower()
    
    # Validate filename is lowercase
    if output_filename != output_filename.lower():
        raise ValueError(f"Generated filename contains uppercase characters: {output_filename}")
    
    return output_filename

def process_all_xlsx_in_directory():
    # Get all .xlsx files in the Input directory
    xlsx_files = glob.glob("Input/*.xlsx")
    
    for xlsx_file in xlsx_files:
        print(f"\nProcessing file: {xlsx_file}")
        
        # Read the file
        df = pd.read_excel(xlsx_file)
        print("Columns found in Excel file:", df.columns.tolist())
        
        # Generate output filename
        base_name = os.path.basename(xlsx_file)
        output_filename = generate_output_filename(base_name)
        output_xml = os.path.join("Output", output_filename).lower()
        print(f"Generated output filename: {output_filename}")
        print(f"Final output path: {output_xml}")
        
        # Transform the .xlsx file to .xml
        create_perfect_edgar_xml(xlsx_file, output_xml)

if __name__ == "__main__":
    process_all_xlsx_in_directory()
