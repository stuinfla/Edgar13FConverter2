import pandas as pd
from xml.etree.ElementTree import Element, SubElement, ElementTree, tostring
import os
import glob
import xml.dom.minidom as minidom
import re

def create_perfect_edgar_xml(input_xlsx, output_xml):
    # Read the Excel file
    df = pd.read_excel(input_xlsx)
    
    # Create the root element with prefixed namespace
    root = Element("ns1:informationTable", attrib={
        "xmlns:ns1": "http://www.sec.gov/edgar/document/thirteenf/informationtable"
    })

    # Iterate through each row in the dataframe
    for _, row in df.iterrows():
        # Create an infoTable entry
        info_table = SubElement(root, "ns1:infoTable")
        
        # Map the fields with the required namespace prefix
        SubElement(info_table, "ns1:nameOfIssuer").text = str(row["Name of Issuer"]).strip()
        SubElement(info_table, "ns1:titleOfClass").text = str(row["Title of Class"]).strip()
        SubElement(info_table, "ns1:cusip").text = str(row["Cusip"]).strip()
        # Round value to nearest dollar as per SEC requirements
        value = round(float(row["Value (to the nearest dollar)"]))
        SubElement(info_table, "ns1:value").text = str(int(value)).strip()
        
        # Nested element for shares or principal amount
        shrs_or_prn_amt = SubElement(info_table, "ns1:shrsOrPrnAmt")
        SubElement(shrs_or_prn_amt, "ns1:sshPrnamt").text = str(int(row["Shares or Principal Amount"])).strip()
        SubElement(shrs_or_prn_amt, "ns1:sshPrnamtType").text = str(row["Shares/Principal"]).strip()
        
        # Optional elements with conditional inclusion
        if pd.notnull(row.get("put/call", None)):
            SubElement(info_table, "ns1:putCall").text = str(row["put/call"]).strip()
        
        SubElement(info_table, "ns1:investmentDiscretion").text = str(row["Investment Discretion"]).strip()
        
        if pd.notnull(row.get("Other Managers", None)):
            SubElement(info_table, "ns1:otherManager").text = str(int(row["Other Managers"])).strip()
        
        # Nested element for voting authority
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
    """Generate output filename in the format 'zen1q2413f.xml'"""
    # Remove file extension and spaces
    base_name = os.path.splitext(input_filename)[0]
    # Convert to lowercase and remove special characters
    clean_name = re.sub(r"[^a-z0-9]", "", base_name.lower())
    # Ensure the filename starts with 'zen'
    if not clean_name.startswith("zen"):
        clean_name = "zen" + clean_name
    return f"{clean_name}.xml"

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
        output_xml = os.path.join("Output", output_filename)
        print(f"Generated output filename: {output_filename}")
        
        # Transform the .xlsx file to .xml
        create_perfect_edgar_xml(xlsx_file, output_xml)

if __name__ == "__main__":
    process_all_xlsx_in_directory()
