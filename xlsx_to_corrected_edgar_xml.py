import pandas as pd
from xml.etree.ElementTree import Element, SubElement, ElementTree, tostring
import os
import glob
import xml.dom.minidom as minidom
import re

# Define mappings for expected Excel column headers, their synonyms, and requirements
COLUMN_MAPPINGS = {
    "name_of_issuer": {"primary": "Name of Issuer", "synonyms": ["Issuer Name", "Security Name"], "required": True},
    "title_of_class": {"primary": "Title of Class", "synonyms": ["Class Title", "Security Type"], "required": True},
    "cusip": {"primary": "Cusip", "synonyms": ["CUSIP ID"], "required": True},
    "figi": {"primary": "FIGI", "synonyms": [], "required": False},
    "value_col": {"primary": "Value (to the nearest dollar)", "synonyms": ["Value", "Market Value"], "required": True, "is_numeric": True, "numeric_type": float},
    "shares_amount_col": {"primary": "Shares or Principal Amount", "synonyms": ["Shares", "Principal Amount", "Quantity"], "required": True, "is_numeric": True, "numeric_type": int},
    "shares_type_col": {"primary": "Shares/Principal", "synonyms": ["Shrs/Prn Typ", "Type", "SH/PRN", "Amount Type"], "required": True, "positional_fallback": "Unnamed: 5"},
    "put_call": {"primary": "put/call", "synonyms": ["Put/Call Option"], "required": False},
    "investment_discretion_col": {"primary": "Investment Discretion", "synonyms": ["Discretion"], "required": True, "positional_fallback": "Unnamed: 6"},
    "other_managers_col": {"primary": "Other Managers", "synonyms": ["Other Manager"], "required": False, "is_numeric": True, "numeric_type": int},
    "sole_voting_col": {"primary": "Sole", "synonyms": ["Sole Voting"], "required": True, "is_numeric": True, "numeric_type": int, "positional_fallback": "Unnamed: 7"},
    "shared_voting_col": {"primary": "Shared", "synonyms": ["Shared Voting"], "required": True, "is_numeric": True, "numeric_type": int, "positional_fallback": "Unnamed: 8"},
    "none_voting_col": {"primary": "None", "synonyms": ["No Voting", "None Voting"], "required": False, "is_numeric": True, "numeric_type": int, "positional_fallback": "Unnamed: 9"}, # Assuming 'None' might be Unnamed: 9 if pattern continues
}

def find_actual_column_name(df_columns, primary_name, synonyms, positional_fallback=None):
    """Try to find the actual column name in df_columns using primary_name, synonyms (case-insensitive), or positional fallback."""
    df_columns_lower_map = {col.lower(): col for col in df_columns} # Preserve original casing
    
    # 1. Try primary name (case-insensitive)
    primary_name_lower = primary_name.lower()
    if primary_name_lower in df_columns_lower_map:
        return df_columns_lower_map[primary_name_lower]
    
    # 2. Try synonyms (case-insensitive)
    for syn in synonyms:
        syn_lower = syn.lower()
        if syn_lower in df_columns_lower_map:
            return df_columns_lower_map[syn_lower]
            
    # 3. Try positional fallback if provided and column exists
    if positional_fallback and positional_fallback in df_columns:
        # This check ensures the 'Unnamed: X' column actually exists in the df
        return positional_fallback
        
    return None

def create_perfect_edgar_xml(input_xlsx, output_xml):
    # Read the Excel file
    df = pd.read_excel(input_xlsx)
    df_columns = df.columns.tolist()

    resolved_cols = {}
    missing_required_cols = []

    for field_key, mapping in COLUMN_MAPPINGS.items():
        actual_name = find_actual_column_name(df_columns, 
                                              mapping["primary"], 
                                              mapping["synonyms"],
                                              mapping.get("positional_fallback")) # Pass fallback
        if actual_name:
            resolved_cols[field_key] = actual_name
        elif mapping["required"]:
            missing_required_cols.append(f"'{mapping['primary']}' (or synonyms like {', '.join(mapping['synonyms']) if mapping['synonyms'] else 'N/A'})")

    if missing_required_cols:
        raise ValueError(f"Missing required Excel columns: {'; '.join(missing_required_cols)}.")

    # Pre-process numeric columns to handle NaN and ensure correct types, using resolved names
    # Value (to the nearest dollar)
    value_actual_col = resolved_cols.get("value_col")
    if value_actual_col:
        df[value_actual_col] = pd.to_numeric(df[value_actual_col], errors='coerce').fillna(0.0)

    # Integer columns - combining logic for all numeric int types
    integer_field_keys = [k for k, v in COLUMN_MAPPINGS.items() if v.get("is_numeric") and v.get("numeric_type") == int]
    
    for field_key in integer_field_keys:
        actual_col_name = resolved_cols.get(field_key)
        if actual_col_name and actual_col_name in df.columns: 
             # Special handling for 'Other Managers' which might be non-numeric initially based on previous logic
            if field_key == 'other_managers_col' and not pd.api.types.is_numeric_dtype(df[actual_col_name]):
                df[actual_col_name] = df[actual_col_name].apply(lambda x: int(float(x)) if str(x).strip().replace('.', '', 1).isdigit() else 0)
            else:
                df[actual_col_name] = pd.to_numeric(df[actual_col_name], errors='coerce').fillna(0).astype(int)

    # Create the root element with proper namespace declaration and prefix
    root = Element("ns1:informationTable", attrib={
        "xmlns:ns1": "http://www.sec.gov/edgar/document/thirteenf/informationtable",
        "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance"
    })

    # Iterate through each row in the dataframe
    for _, row in df.iterrows():
        # Create an infoTable entry with namespace prefix
        info_table = SubElement(root, "ns1:infoTable")
        
        # Required fields with namespace prefix, using resolved column names
        SubElement(info_table, "ns1:nameOfIssuer").text = str(row[resolved_cols["name_of_issuer"]]).strip()
        SubElement(info_table, "ns1:titleOfClass").text = str(row[resolved_cols["title_of_class"]]).strip()
        SubElement(info_table, "ns1:cusip").text = str(row[resolved_cols["cusip"]]).strip()
        
        # Optional FIGI field with namespace prefix
        figi_actual_col = resolved_cols.get("figi")
        if figi_actual_col and pd.notnull(row.get(figi_actual_col, None)):
            SubElement(info_table, "ns1:figi").text = str(row[figi_actual_col]).strip()
        
        # Value rounded to nearest dollar with namespace prefix
        value_data = 0 
        if value_actual_col:
             value_data = round(float(row[value_actual_col]))
        SubElement(info_table, "ns1:value").text = str(int(value_data)).strip()
        
        # Shares or principal amount with namespace prefix
        shrs_or_prn_amt = SubElement(info_table, "ns1:shrsOrPrnAmt")
        SubElement(shrs_or_prn_amt, "ns1:sshPrnamt").text = str(row[resolved_cols["shares_amount_col"]]).strip()
        SubElement(shrs_or_prn_amt, "ns1:sshPrnamtType").text = str(row[resolved_cols["shares_type_col"]]).strip()
        
        # Optional put/call field with namespace prefix
        put_call_actual_col = resolved_cols.get("put_call")
        if put_call_actual_col and pd.notnull(row.get(put_call_actual_col, None)):
            SubElement(info_table, "ns1:putCall").text = str(row[put_call_actual_col]).strip()
        
        # Required investment discretion with namespace prefix
        SubElement(info_table, "ns1:investmentDiscretion").text = str(row[resolved_cols["investment_discretion_col"]]).strip()
        
        # Optional other manager field with namespace prefix
        other_managers_actual_col = resolved_cols.get("other_managers_col")
        if other_managers_actual_col and pd.notnull(row.get(other_managers_actual_col, None)):
            SubElement(info_table, "ns1:otherManager").text = str(row[other_managers_actual_col]).strip()
        
        # Voting authority with namespace prefix
        voting_authority = SubElement(info_table, "ns1:votingAuthority")
        SubElement(voting_authority, "ns1:Sole").text = str(row[resolved_cols["sole_voting_col"]]).strip()
        SubElement(voting_authority, "ns1:Shared").text = str(row[resolved_cols["shared_voting_col"]]).strip()
        
        # Handle None voting (now optional, defaults to 0 if not found)
        none_voting_value = 0 # Default to 0
        none_voting_actual_col = resolved_cols.get("none_voting_col")
        if none_voting_actual_col: # If column was resolved
            none_voting_value = row[none_voting_actual_col] # Value is already pre-processed to int
        SubElement(voting_authority, "ns1:None").text = str(none_voting_value).strip()
    
    # Convert the XML tree to a string with proper indentation
    raw_xml = tostring(root, encoding="utf-8", method="xml")
    pretty_xml = minidom.parseString(raw_xml).toprettyxml(indent="	", encoding="utf-8")
    
    # Write the XML to file with standalone="yes" in the declaration
    with open(output_xml, "wb") as file:
        file.write(b'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n')
        pretty_xml = pretty_xml.replace(b'<?xml version="1.0" encoding="utf-8"?>\n', b'')
        file.write(pretty_xml.strip())
    print(f"Perfect EDGAR-compliant XML file created: {output_xml}")

def generate_output_filename(input_filename):
    """Generate output filename in SEC-compliant format"""
    input_filename = input_filename.lower()
    
    base_name = os.path.splitext(input_filename)[0]
    
    clean_name = re.sub(r"[^a-z0-9]", "", base_name)
    
    if not clean_name.endswith("13f"):
        clean_name += "13f"
    
    if not re.search(r"q\d{2}", clean_name):
        today = pd.Timestamp.today()
        quarter = (today.month - 1) // 3 + 1
        year = today.year % 100
        clean_name += f"q{quarter}{year:02d}"
    
    output_filename = f"{clean_name}.xml".lower()
    
    if output_filename != output_filename.lower():
        raise ValueError(f"Generated filename contains uppercase characters: {output_filename}")
    
    return output_filename

def process_all_xlsx_in_directory():
    xlsx_files = glob.glob("Input/*.xlsx")
    
    for xlsx_file in xlsx_files:
        print(f"\nProcessing file: {xlsx_file}")
        
        df = pd.read_excel(xlsx_file)
        print("Columns found in Excel file:", df.columns.tolist())
        
        base_name = os.path.basename(xlsx_file)
        output_filename = generate_output_filename(base_name)
        output_xml = os.path.join("Output", output_filename).lower()
        print(f"Generated output filename: {output_filename}")
        print(f"Final output path: {output_xml}")
        
        create_perfect_edgar_xml(xlsx_file, output_xml)

if __name__ == "__main__":
    process_all_xlsx_in_directory()
