import pandas as pd
from xml.etree.ElementTree import Element, SubElement, ElementTree, tostring
import os
import glob
import xml.dom.minidom as minidom
import re

# Define mappings for expected Excel column headers, their synonyms, and requirements
COLUMN_MAPPINGS = {
    "name_of_issuer": {"primary": "Name of Issuer", "synonyms": ["Issuer Name", "Security Name"], "required": True},
    "title_of_class": {"primary": "Title of Class", "synonyms": ["Instrument Subtype", "Equity", "Debt", "Option", "Class Title", "Security Type"], "required": True},
    "cusip": {"primary": "Cusip", "synonyms": ["CUSIP ID", "CUSIP/CINS"], "required": True},
    "figi": {"primary": "FIGI", "synonyms": [], "required": False},
    "value_col": {"primary": "Value (to the nearest dollar)", "synonyms": ["Value", "Market Value"], "required": True, "is_numeric": True, "numeric_type": float},
    "shares_amount_col": {"primary": "Shares or Principal Amount", "synonyms": ["Shares", "Principal Amount", "Quantity", "Shares Amount"], "required": True, "is_numeric": True, "numeric_type": int},
    "shares_type_col": {"primary": "Shares/Principal", "synonyms": ["Shrs/Prn Typ", "Type", "SH/PRN", "Amount Type", "Share Type"], "required": True, "positional_fallback": "Unnamed: 5"},
    "put_call": {"primary": "put/call", "synonyms": ["Put/Call Option", "Put Call Indicator"], "required": False},
    "investment_discretion_col": {"primary": "Investment Discretion", "synonyms": ["Discretion"], "required": True, "positional_fallback": "Unnamed: 6"},
    "other_managers_col": {"primary": "Other Managers", "synonyms": ["Other Manager"], "required": False, "is_numeric": True, "numeric_type": int, "positional_fallback": "Unnamed: 7"},
    "sole_voting_col": {"primary": "Sole", "synonyms": ["Sole Voting", "Voting Authority Sole"], "required": True, "is_numeric": True, "numeric_type": int, "positional_fallback": "Unnamed: 8"},
    "shared_voting_col": {"primary": "Shared", "synonyms": ["Shared Voting", "Voting Authority Shared"], "required": True, "is_numeric": True, "numeric_type": int, "positional_fallback": "Unnamed: 9"},
    "none_voting_col": {"primary": "None", "synonyms": ["No Voting", "None Voting", "Voting Authority None"], "required": False, "is_numeric": True, "numeric_type": int, "positional_fallback": "Unnamed: 10"}
}

def find_actual_column_name(df_columns, primary_name, synonyms, positional_fallback=None):
    """Try to find the actual column name in df_columns using primary_name, synonyms (case-insensitive, stripped),
       the positional_fallback name, or the column at the index specified by positional_fallback."""
    # Create a map of lowercased, stripped DataFrame column names to their original casing
    # This handles cases where Excel column names might have leading/trailing spaces
    df_columns_lower_map = {col.lower().strip(): col for col in df_columns}

    # 1. Try primary name (case-insensitive, stripped)
    primary_name_lower_stripped = primary_name.lower().strip()
    if primary_name_lower_stripped in df_columns_lower_map:
        return df_columns_lower_map[primary_name_lower_stripped]

    # 2. Try synonyms (case-insensitive, stripped)
    for syn in synonyms:
        syn_lower_stripped = syn.lower().strip()
        if syn_lower_stripped in df_columns_lower_map:
            return df_columns_lower_map[syn_lower_stripped]

    # 3. & 4. Try positional fallback strategies if provided
    if positional_fallback:
        # 3. Try the positional_fallback name itself (e.g., "Unnamed: 9") (case-insensitive, stripped)
        positional_fallback_lower_stripped = positional_fallback.lower().strip()
        if positional_fallback_lower_stripped in df_columns_lower_map:
            return df_columns_lower_map[positional_fallback_lower_stripped]

        # 4. Try column at the numerical index derived from positional_fallback string (e.g., "Unnamed: 9" -> index 9)
        #    This regex extracts the number from patterns like "Unnamed: X", "ColumnX", etc.
        match = re.search(r'(\d+)$', positional_fallback)
        if match:
            try:
                idx = int(match.group(1))
                # Check if the derived index is valid for the df_columns list
                if 0 <= idx < len(df_columns):
                    # If a column exists at this index, assume it's the one we want.
                    print(f"    --> Positional fallback by index: Using column '{df_columns[idx]}' at index {idx} for expected '{primary_name}' (fallback pattern '{positional_fallback}')")
                    return df_columns[idx]
            except ValueError:
                # This should ideally not happen if regex matches \d+
                print(f"    --> Warning: Could not parse index from positional_fallback '{positional_fallback}' for '{primary_name}'.")
                pass # Continue to return None if parsing fails

    return None

def create_perfect_edgar_xml(input_xlsx, output_xml):
    print(f"\n--- Debugging for {input_xlsx} ---")
    # Read the Excel file, explicitly setting header to row 0
    df = pd.read_excel(input_xlsx, header=0)
    df_columns = df.columns.tolist()
    print(f"Excel columns found in '{input_xlsx}' (using header=0): {df_columns}")

    resolved_cols = {}
    missing_required_cols = []
    print("--- Attempting to resolve column names: ---")
    for field_key, mapping in COLUMN_MAPPINGS.items():
        actual_name = find_actual_column_name(df_columns,
                                              mapping["primary"],
                                              mapping["synonyms"],
                                              mapping.get("positional_fallback")) # Pass fallback
        print(f"  For mapping key '{field_key}' (Primary: '{mapping['primary']}'): Resolved Excel column name = '{actual_name}'")
        if actual_name:
            resolved_cols[field_key] = actual_name
        elif mapping["required"]:
            missing_required_cols.append(f"'{mapping['primary']}' (or synonyms like {', '.join(mapping['synonyms']) if mapping['synonyms'] else 'N/A'})")

    if missing_required_cols:
        raise ValueError(f"Missing required Excel columns: {'; '.join(missing_required_cols)}.")

    print(f"--- Final resolved column map for '{input_xlsx}': {resolved_cols} ---")

    # Display relevant parts of the DataFrame before numeric conversion
    # Filter to only show columns that were successfully resolved AND exist in the DataFrame
    display_columns = [col for col in resolved_cols.values() if col in df.columns]
    if display_columns:
        print(f"--- DataFrame head (first 3 rows) BEFORE numeric conversion for '{input_xlsx}' (showing resolved & existing columns): ---")
        try:
            print(df[display_columns].head(3).to_string())
        except Exception as e:
            print(f"Error printing DataFrame head with resolved columns: {e}")
            print(f"Problematic display_columns list: {display_columns}")
    else:
        print(f"--- DataFrame head for '{input_xlsx}': No valid resolved columns to display or an issue with resolved names. All columns head (first 3 rows): ---")
        print(df.head(3).to_string())

    # Pre-process numeric columns to handle NaN and ensure correct types, using resolved names
    # Value (to the nearest dollar)
    value_actual_col = resolved_cols.get("value_col")
    if value_actual_col:
        df[value_actual_col] = pd.to_numeric(df[value_actual_col], errors='coerce').fillna(0.0)

    # Integer columns - combining logic for all numeric int types
    integer_field_keys = [k for k, v in COLUMN_MAPPINGS.items() if v.get("is_numeric") and v.get("numeric_type") == int]

    # Display relevant parts of the DataFrame AFTER numeric conversion
    if display_columns: # Re-use display_columns from before, assuming they are still relevant
        print(f"--- DataFrame head (first 3 rows) AFTER numeric conversion for '{input_xlsx}' (showing resolved & existing columns): ---")
        try:
            print(df[display_columns].head(3).to_string())
        except Exception as e:
            print(f"Error printing DataFrame head after numeric conversion: {e}")
            print(f"Problematic display_columns list: {display_columns}")
    else:
        print(f"--- DataFrame head for '{input_xlsx}' after numeric: No valid resolved columns. All columns head (first 3 rows): ---")
        print(df.head(3).to_string())

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
