import pandas as pd
from lxml import etree
import datetime
from datetime import timezone # Added for timezone.utc
import os
import numpy as np
import argparse
from dataclasses import dataclass, field
from typing import List, Optional

# Path to your XSD schema file
XSD_FILE_PATH = "/Users/stuartkerr/Library/CloudStorage/OneDrive-Personal/Code/EXCEL TO EDGAR XML/Finra 6151 requirements/oh-20191231.xsd"

# --- NEW Helper functions for formatting based on XSD types ---
def format_pct_or_nm(value) -> str:
    """Formats a number to a string compliant with PctOrNmType.
    (e.g., "25.50", "0.00", or "" if not meaningful).
    Handles np.nan or empty strings from Excel.
    """
    if pd.isna(value) or str(value).strip() == "":
        return ""
    try:
        num = float(value)
        # Format to ensure at least two decimal places, e.g., 0 -> "0.00", 25.5 -> "25.50"
        # The XSD PctType implies at least two decimal places: <xs:pattern value="[0-9]*\.[0-9]{2,}"/>
        return f"{num:.2f}" # Standard rounding to 2 decimal places
    except ValueError:
        return "" # If conversion to float fails, treat as not meaningful

def format_decimal2_or_nm(value) -> str:
    """Formats a number to a string compliant with Decimal2OrNmType.
    (e.g., "123.45", "-5.50", "0.00", or "" if not meaningful).
    """
    if pd.isna(value) or str(value).strip() == "":
        return ""
    try:
        num = float(value)
        return f"{num:.2f}" # Ensure two decimal places
    except ValueError:
        return ""

def format_cph4_or_nm(value) -> str:
    """Formats a number to a string compliant with CphType.
    (e.g., "123.4567", "-5.1234", "0.0000", or "" if not meaningful).
    """
    if pd.isna(value) or str(value).strip() == "":
        return ""
    try:
        num = float(value)
        return f"{num:.4f}" # Ensure four decimal places
    except ValueError:
        return ""

# --- NEW Data Classes Aligned with oh-20191231.xsd for nmsHeldOrderRoutingReport --- 

@dataclass
class VenueData: # Corresponds to OH_VENUE_DATA in XSD
    venue_name: str
    market_order_pct: Optional[str] = None        # PctOrNmType, will be formatted by format_pct_or_nm
    marketable_limit_order_pct: Optional[str] = None # PctOrNmType, will be formatted by format_pct_or_nm
    non_marketable_limit_order_pct: Optional[str] = None # PctOrNmType, will be formatted by format_pct_or_nm
    other_order_pct: Optional[str] = None         # PctOrNmType, will be formatted by format_pct_or_nm
    net_pmt_paid_recv_market_orders_usd: Optional[float] = None
    net_pmt_paid_recv_market_orders_cph: Optional[float] = None
    net_pmt_paid_recv_marketable_limit_orders_usd: Optional[float] = None
    net_pmt_paid_recv_marketable_limit_orders_cph: Optional[float] = None
    net_pmt_paid_recv_non_marketable_limit_orders_usd: Optional[float] = None
    net_pmt_paid_recv_non_marketable_limit_orders_cph: Optional[float] = None
    net_pmt_paid_recv_other_orders_usd: Optional[float] = None
    net_pmt_paid_recv_other_orders_cph: Optional[float] = None
    payment_disclosure_link: Optional[str] = None # xs:anyURI
    mic: Optional[str] = None                # MicType (optional)
    mpid: Optional[str] = None               # MpidType (optional)

class CategorySummaryData: # Corresponds to the summary part of OH_CATEGORY_DATA
    def __init__(self,
                 market_order_pct: str,
                 marketable_limit_order_pct: str,
                 non_marketable_limit_order_pct: str,
                 other_order_pct: str):
        self.market_order_pct = market_order_pct
        self.marketable_limit_order_pct = marketable_limit_order_pct
        self.non_marketable_limit_order_pct = non_marketable_limit_order_pct
        self.other_order_pct = other_order_pct

class SecurityCategoryData: # Corresponds to OH_CATEGORY_DATA
    # name is CategoryNameType (e.g., "NMS Stock")
    def __init__(self, name: str, summary: CategorySummaryData, venues: list[VenueData]):
        self.name = name
        self.summary = summary
        self.venues = venues

class NmsHeldOrderRoutingReportData: # Root element: nmsHeldOrderRoutingReport
    def __init__(self,
                 version: str,        # e.g., "1.3"
                 firm_name: str,      # BrokerDealerNameType
                 year: str,           # YearType e.g. "2023"
                 qtr: str,            # QuarterType e.g. "1"
                 s_non_directed_categories: list[SecurityCategoryData], # Optional, for <sNonDirected><categoryList>
                 s_directed_categories: list[SecurityCategoryData]):   # Optional, for <sDirected><categoryList>
        self.version = version
        self.firm_name = firm_name
        self.year = year
        self.qtr = qtr
        self.s_non_directed_categories = s_non_directed_categories if s_non_directed_categories is not None else []
        self.s_directed_categories = s_directed_categories if s_directed_categories is not None else []

# --- XML Element Creation Helper (may need adjustments for new structure) ---
def _add_element(parent, tag_name, text_content=None):
    element = etree.SubElement(parent, tag_name)
    if text_content is not None:
        element.text = str(text_content) # Ensure content is string
    return element

# --- Helper function to get first month of a quarter ---
def get_first_month_of_quarter(quarter_str: str) -> str:
    """Returns the first month number (1, 4, 7, 10) for a given quarter string ('1'-'4')."""
    q_map = {"1": "1", "2": "4", "3": "7", "4": "10"}
    return q_map.get(str(quarter_str).strip(), "1") # Default to 1 if invalid

# --- Placeholder Excel Parsing Functions (Needs Robust Implementation) ---
# These functions would populate instances of SecurityCategoryData from the Excel sheet.

def _parse_single_security_category(df, category_name_in_excel, category_xml_tag_name, common_material_aspects):
    """Parses data for a single security category from the main DataFrame."""
    category_data = SecurityCategoryData(category_xml_tag_name, CategorySummaryData("", "", "", ""), [])
    print(f"\nAttempting to parse section: '{category_name_in_excel}'")

    try:
        df_col0_str = df.iloc[:, 0].astype(str).str.strip()
        category_start_rows = df[df_col0_str == category_name_in_excel].index

        if not category_start_rows.any():
            print(f"Warning: Category section title '{category_name_in_excel}' not found in Column A.")
            return category_data
        
        category_start_idx = category_start_rows[0]
        print(f"Located '{category_name_in_excel}' starting at DataFrame index: {category_start_idx}")

        # Try to find the 'Summary' label row for this category
        summary_label_rows = df[(
            df.iloc[:, 0].astype(str).str.strip().str.lower() == "summary") & 
            (df.index > category_start_idx)
        ]

        if not summary_label_rows.empty:
            summary_label_idx = summary_label_rows.index[0]
            # The actual data is expected two rows below the 'Summary' label row 
            # (Summary Label -> Summary Headers -> Summary Data Values)
            summary_data_actual_idx = summary_label_idx + 2

            if summary_data_actual_idx < len(df):
                summary_values_row = df.iloc[summary_data_actual_idx]
                try:
                    # Determine the starting column index for NDO data
                    first_cell_value_ndo = str(summary_values_row.iloc[0]).strip()
                    ndo_data_start_col_idx = 0 # Default, will be updated if first cell is not numeric
                    try:
                        # Attempt to convert the first cell to numeric.
                        # If it's a number (like '100' for Options summary), data starts at iloc[0].
                        pd.to_numeric(first_cell_value_ndo)
                        ndo_data_start_col_idx = 0 
                    except ValueError:
                        # If it's not numeric (like a label 'Non-Directed Orders...'), data starts at iloc[1].
                        ndo_data_start_col_idx = 1
                    
                    # More targeted debug print for clarity during testing
                    if category_name_in_excel == "Options" or category_name_in_excel == "S&P 500 Stocks": # Limit debug noise
                        print(f"DEBUG {category_name_in_excel}: NDO data using start_col_idx: {ndo_data_start_col_idx} (first cell was: '{first_cell_value_ndo}')")

                    num_cols_in_row = len(summary_values_row)

                    # Parse NDO percentages using the determined start index, with bounds checking
                    if num_cols_in_row > ndo_data_start_col_idx:
                        category_data.summary.market_order_pct = format_pct_or_nm(summary_values_row.iloc[ndo_data_start_col_idx])
                    else:
                        category_data.summary.market_order_pct = ""

                    if num_cols_in_row > ndo_data_start_col_idx + 1:
                        category_data.summary.marketable_limit_order_pct = format_pct_or_nm(summary_values_row.iloc[ndo_data_start_col_idx + 1])
                    else:
                        category_data.summary.marketable_limit_order_pct = ""

                    if num_cols_in_row > ndo_data_start_col_idx + 2:
                        category_data.summary.non_marketable_limit_order_pct = format_pct_or_nm(summary_values_row.iloc[ndo_data_start_col_idx + 2])
                    else:
                        category_data.summary.non_marketable_limit_order_pct = ""

                    if num_cols_in_row > ndo_data_start_col_idx + 3:
                        category_data.summary.other_order_pct = format_pct_or_nm(summary_values_row.iloc[ndo_data_start_col_idx + 3])
                    else:
                        category_data.summary.other_order_pct = ""

                except Exception as e:
                    print(f"Error parsing NDO summary data for {category_name_in_excel} at row index {summary_data_actual_idx}: {e}")
            else:
                print(f"Warning: Calculated summary data row index {summary_data_actual_idx} is out of bounds for '{category_name_in_excel}'.")
        else:
            print(f"Warning: 'Summary' label row not found for '{category_name_in_excel}' after index {category_start_idx}. NDO percentages will remain default.")

        # Find the 'Venues' label to determine where venue data starts
        venues_label_rows = df[(
            df.iloc[:, 0].astype(str).str.strip().str.lower() == "venues") & 
            (df.index > category_start_idx)
        ]
        
        if venues_label_rows.empty:
            print(f"Warning: 'Venues' label not found for '{category_name_in_excel}'. Attempting to find venues starting from a default offset.")
            # Fallback: assume venues start a few rows after category title if 'Venues' label is missing.
            # This is a guess. Category Title -> Summary Label -> Summary Headers -> Summary Data -> Blank Row -> Venues Label (expected)
            # If Venues label is missing, let's try category_start_idx + 5 or so.
            # However, the loop below should handle finding the first actual venue name.
            # For now, we'll set a nominal start and let the venue name check drive the loop.
            venue_data_start_idx = category_start_idx + 2 # Heuristic, likely needs to be higher
            # A better heuristic would be after the summary block, if parsed.
            if 'summary_data_actual_idx' in locals() and summary_data_actual_idx:
                 venue_data_start_idx = summary_data_actual_idx + 2 # After summary data values + 1 blank row (guess)
            else: # If no summary data, maybe after category title + 1 (if category title is the only header)
                 venue_data_start_idx = category_start_idx + 1
        else:
            venues_label_idx = venues_label_rows.index[0]
            venue_data_start_idx = venues_label_idx + 2 # Venues data starts 2 rows after 'Venues' label (Label -> Headers -> Data)

        # Helper function to get and convert cell values for venues
        def get_value_from_row(row_data, column_index, is_percentage_val=False, default_return_val=np.nan):
            try:
                cell_value_str = str(row_data.iloc[column_index]).strip()
                if cell_value_str == "":
                    # print(f"DEBUG get_value_from_row: Empty string for col {column_index}, treating as 0.0")
                    return 0.0  # Treat genuinely empty strings (that Excel might format as 0) as 0.0
                
                numeric_value = pd.to_numeric(cell_value_str, errors='coerce')
                
                if pd.isna(numeric_value):
                    # print(f"DEBUG get_value_from_row: Coercion to NaN for col {column_index}, val '{cell_value_str}'")
                    return np.nan # Return NaN if coercion failed (e.g. for 'N/A')
                
                if is_percentage_val:
                    return numeric_value / 100.0
                return numeric_value
            except IndexError:
                # print(f"WARN: IndexError for col {column_index} in {category_name_in_excel} venues. Row: {row_data.iloc[0] if len(row_data)>0 else 'Unknown'}")
                return default_return_val
            except Exception as e:
                # print(f"ERROR: Unexpected error in get_value_from_row (col {column_index}, val '{row_data.iloc[column_index] if column_index < len(row_data) else 'OOB'}'): {e}")
                return default_return_val

        # Parse venue data
        empty_row_counter = 0
        for idx in range(venue_data_start_idx, len(df)):
            current_row_values = df.iloc[idx]
            venue_name_raw = current_row_values.iloc[0]

            if pd.isna(venue_name_raw) or str(venue_name_raw).strip() == "":
                if current_row_values.isna().all() or (str(df.iloc[idx,0]).strip() == "" and all(pd.isna(df.iloc[idx,j]) for j in range(1,df.shape[1]))):
                    print(f"End of venue data for '{category_name_in_excel}' at index {idx} (empty or mostly empty row).")
                    break
                # If first cell is empty but others might have data, treat as end of venues for this section
                print(f"End of venue data for '{category_name_in_excel}' at index {idx} (first cell empty).")
                break

            venue_name = str(venue_name_raw).strip()
            
            if venue_name in ["S&P 500 Stocks", "Non-S&P 500 stocks", "Options", "2nd Quarter, 2024"] or venue_name.startswith("Outset does not have"):
                print(f"End of venue data for '{category_name_in_excel}' at index {idx} (new section/footer found: '{venue_name}').")
                break

            venue_item = VenueData(
                venue_name=get_value_from_row(current_row_values, 0),
                market_order_pct=format_pct_or_nm(get_value_from_row(current_row_values, 1, is_percentage_val=True)), # Excel Col B
                marketable_limit_order_pct=format_pct_or_nm(get_value_from_row(current_row_values, 2, is_percentage_val=True)), # Excel Col C
                non_marketable_limit_order_pct=format_pct_or_nm(get_value_from_row(current_row_values, 3, is_percentage_val=True)), # Excel Col D
                other_order_pct=format_pct_or_nm(get_value_from_row(current_row_values, 4, is_percentage_val=True)), # Excel Col E
                
                # USD payment fields from Excel columns F, G, H, I
                net_pmt_paid_recv_market_orders_usd=get_value_from_row(current_row_values, 5), # Excel Col F
                net_pmt_paid_recv_marketable_limit_orders_usd=get_value_from_row(current_row_values, 6), # Excel Col G
                net_pmt_paid_recv_non_marketable_limit_orders_usd=get_value_from_row(current_row_values, 7), # Excel Col H
                net_pmt_paid_recv_other_orders_usd=get_value_from_row(current_row_values, 8), # Excel Col I
                
                # CPH fields are not present per venue in Excel, so set to None
                net_pmt_paid_recv_market_orders_cph=None,
                net_pmt_paid_recv_marketable_limit_orders_cph=None,
                net_pmt_paid_recv_non_marketable_limit_orders_cph=None,
                net_pmt_paid_recv_other_orders_cph=None,
                
                payment_disclosure_link="Does not have a profit sharing arrangement with or receive rebates or payments for order flow from any of the above venues/market centers.",
                mic="", # Placeholder, remains empty as per user guidance
                mpid="" # Placeholder, remains empty as per user guidance
            )
            category_data.venues.append(venue_item)
            print(f"Added venue: {venue_name}")

    except Exception as e:
        print(f"Error parsing category '{category_name_in_excel}': {e}")
        import traceback
        traceback.print_exc() # Add traceback for debugging
    
    return category_data

def parse_excel_data(excel_filepath, material_aspects_text, firm_name_param, report_year_param, report_qtr_param):
    """Parses the entire Excel file and returns a NmsHeldOrderRoutingReportData object."""
    print(f"Reading Excel file: {excel_filepath}")
    try:
        df = pd.read_excel(excel_filepath, header=None)  # Read without headers initially
    except FileNotFoundError:
        print(f"Error: Excel file not found at {excel_filepath}")
        return None
    except Exception as e:
        print(f"Error reading Excel file {excel_filepath}: {e}")
        return None

    # Use passed parameters for report metadata
    quarterly_data_for_months = NmsHeldOrderRoutingReportData(
        version="1.3", # Per XSD examples and common usage for this version of the schema
        firm_name=str(firm_name_param),
        year=str(report_year_param),
        qtr=str(report_qtr_param),
        s_non_directed_categories=[],
        s_directed_categories=[]
    )

    # Placeholder for common material aspects if needed for new structure - currently unused in nmsHeldOrderRoutingReport directly
    common_material_aspects_text = material_aspects_text

    # Example: Assuming these are always non-directed categories based on typical 606(a)(1) reports
    # The category names here ("NMS Stock", "Other OTC Stock", "Option") should match CategoryNameType in XSD
    # The Excel section names ("S&P 500 Stocks", etc.) are used to find data in your specific Excel sheet.
    # If your Excel has different section names, update them below.

    # S&P 500 Stocks -> mapped to "NMS Stock" or a more specific category if XSD allows
    # For now, let's assume standard categories. If XSD has enumerated CategoryNameType, we must use those.
    # From oh-20191231.xsd, CategoryNameType is xs:string, so these names are flexible descriptions.
    # Common practice is to use: "NMS Stock", "Other NMS Stock", "Option"
    # Or more broadly for (a)(1): "S&P 500 Index Stocks", "Other NMS Stocks", "Listed Options"

    # We will map common Excel section names to standardized XSD category names.
    excel_to_xsd_category_map = {
        "S&P 500 Stocks": "NMS Stock", # Or potentially "S&P 500 Index Stocks"
        "Non-S&P 500 stocks": "Other NMS Stock", # Or more general "Other Stock"
        "Options": "Option" # Or "Listed Options"
    }

    for excel_section_name, xsd_category_name in excel_to_xsd_category_map.items():
        category_data = _parse_single_security_category(
            df, excel_section_name, xsd_category_name, common_material_aspects_text
        )
        if category_data:
            quarterly_data_for_months.s_non_directed_categories.append(category_data)
        else:
            print(f"Warning: No data parsed for Excel section '{excel_section_name}' (mapped to XSD category '{xsd_category_name}').")

    # If you have directed orders, you would parse them similarly and append to:
    # quarterly_data_for_months.s_directed_categories.append(...)

    print("Finished parsing Excel data.")
    return quarterly_data_for_months

# --- XSD Validation Function ---
def validate_xml_against_xsd(xml_filepath, xsd_filepath):
    """Validates an XML file against an XSD schema.

    Args:
        xml_filepath (str): The path to the XML file to validate.
        xsd_filepath (str): The path to the XSD schema file.

    Returns:
        tuple: (bool, list) where bool is True if valid, False otherwise,
               and list contains error messages if invalid, or is empty if valid.
    """
    if not os.path.exists(xml_filepath):
        # print(f"Error: XML file not found at {xml_filepath}") # Keep for debugging if needed
        return False, [f"XML file not found at {xml_filepath}"]
    if not os.path.exists(xsd_filepath):
        # print(f"Error: XSD schema file not found at {xsd_filepath}") # Keep for debugging if needed
        return False, [f"XSD schema file not found at {xsd_filepath}"]

    try:
        xml_doc = etree.parse(xml_filepath)
        xsd_doc = etree.parse(xsd_filepath)
        xmlschema = etree.XMLSchema(xsd_doc)

        is_valid = xmlschema.validate(xml_doc)

        if is_valid:
            # print(f"Validation successful: '{os.path.basename(xml_filepath)}' is valid against '{os.path.basename(xsd_filepath)}'.")
            return True, []
        else:
            # print(f"Validation failed: '{os.path.basename(xml_filepath)}' is invalid against '{os.path.basename(xsd_filepath)}'.")
            # print("Validation Errors:")
            error_messages = []
            for error in xmlschema.error_log:
                # print(f"  - Line {error.line}, Column {error.column}: {error.message} (Domain: {error.domain_name}, Type: {error.type_name})")
                error_messages.append(f"Line {error.line}, Col {error.column}: {error.message}")
            return False, error_messages
    except etree.XMLSyntaxError as e:
        # print(f"XML Syntax Error: Could not parse XML file '{os.path.basename(xml_filepath)}'. Error: {e}")
        return False, [f"XML Syntax Error: {e}"]
    except Exception as e:
        # print(f"An unexpected error occurred during validation: {e}")
        return False, [f"Unexpected validation error: {e}"]

# --- Main XML Generation Function ---
def create_finra_6151_xml(excel_filepath, output_xml_filepath, 
                            firm_name, # Used for the <firmName> element
                            reporting_year, reporting_quarter, 
                            material_aspects_text): # Common material aspects text
    """ 
    Main function to parse Excel, build XML structure, and write to file.
    """
    
    # 1. Parse Excel Data into structured objects
    quarterly_report_month_data = parse_excel_data(
        excel_filepath, 
        material_aspects_text, 
        firm_name, 
        reporting_year, 
        reporting_quarter
    )
    if quarterly_report_month_data is None:
        print("Halting XML generation due to Excel parsing error.")
        return

    # 2. Create the root XML element based on XSD (heldOrderRoutingPublicReport)
    root = etree.Element("heldOrderRoutingPublicReport")

    # 3. Add top-level report metadata to the root
    _add_element(root, "version", quarterly_report_month_data.version)
    _add_element(root, "bd", quarterly_report_month_data.firm_name) # 'bd' is broker-dealer
    _add_element(root, "year", quarterly_report_month_data.year)
    _add_element(root, "qtr", quarterly_report_month_data.qtr)
    # timestamp is optional, skipping for now

    # 4. Create one <rMonthly> element (XSD allows 1 to 3)
    # For now, we'll represent the entire quarter's parsed data as the first month's data.
    # Future enhancement: Distribute data if Excel contains true monthly breakouts or replicate if not.
    rMonthly_el = _add_element(root, "rMonthly")
    _add_element(rMonthly_el, "year", quarterly_report_month_data.year) # Year for this monthly section
    _add_element(rMonthly_el, "mon", get_first_month_of_quarter(quarterly_report_month_data.qtr)) # Month for this monthly section

    # 5. Populate <rMonthly> with data from parsed categories (rSP500, rOtherStocks, rOptions)
    # These map to OrderRoutingType in XSD, which matches our CategorySummaryData structure.
    category_to_xsd_element_map = {
        "NMS Stock": "rSP500",
        "Other NMS Stock": "rOtherStocks", # Adjusted from "Other OTC Stock" to align with common XSD usage
        "Option": "rOptions"
    }

    for security_category_data in quarterly_report_month_data.s_non_directed_categories:
        xsd_element_name = category_to_xsd_element_map.get(security_category_data.name)
        if not xsd_element_name:
            print(f"Warning: Unknown category '{security_category_data.name}' found in parsed data. Skipping.")
            continue

        # Create the specific category element (e.g., <rSP500>)
        category_summary_el = _add_element(rMonthly_el, xsd_element_name)
        summary_data = security_category_data.summary

        # Populate elements within e.g. <rSP500> based on CategorySummaryData / OrderRoutingType
        _add_element(category_summary_el, "ndoPct", summary_data.market_order_pct)
        _add_element(category_summary_el, "ndoMarketPct", summary_data.marketable_limit_order_pct)
        _add_element(category_summary_el, "ndoMarketableLimitPct", summary_data.marketable_limit_order_pct)
        _add_element(category_summary_el, "ndoNonmarketableLimitPct", summary_data.non_marketable_limit_order_pct)
        _add_element(category_summary_el, "ndoOtherPct", summary_data.other_order_pct)

        # Add <rVenues> container within the category summary element
        rVenues_el = _add_element(category_summary_el, "rVenues")

        for venue_data in security_category_data.venues:
            rVenue_el = _add_element(rVenues_el, "rVenue") # Each venue is an <rVenue>
            _add_element(rVenue_el, "name", venue_data.venue_name) # CORRECTED from venueName to name
            # Add <orderPct> - Total % of orders in this category routed to this venue.
            # Placeholder: Use empty string for now. User needs to confirm source from Excel.
            _add_element(rVenue_el, "orderPct", format_pct_or_nm("")) 

            # Add other venue-specific fields from VenueData, matching XSD elements for rVenue
            _add_element(rVenue_el, "marketPct", format_pct_or_nm(venue_data.market_order_pct)) 
            _add_element(rVenue_el, "marketableLimitPct", format_pct_or_nm(venue_data.marketable_limit_order_pct))
            _add_element(rVenue_el, "nonMarketableLimitPct", format_pct_or_nm(venue_data.non_marketable_limit_order_pct))
            _add_element(rVenue_el, "otherPct", format_pct_or_nm(venue_data.other_order_pct))
            
            # The following elements (avgExecSize, avgNetExecRate, marketCenterFeeRate) do NOT belong in rVenue.
            # They belong in the parent rSecurityType element (e.g. rSP500).
            # _add_element(rVenue_el, "avgExecSize", "") # REMOVED
            # _add_element(rVenue_el, "avgNetExecRate", "") # REMOVED
            # _add_element(rVenue_el, "marketCenterFeeRate", "") # REMOVED

            # Payment and material aspects elements DO belong in rVenue as per XSD
            _add_element(rVenue_el, "netPmtPaidRecvMarketOrdersUsd", format_decimal2_or_nm(venue_data.net_pmt_paid_recv_market_orders_usd))
            _add_element(rVenue_el, "netPmtPaidRecvMarketOrdersCph", format_cph4_or_nm(venue_data.net_pmt_paid_recv_market_orders_cph))
            _add_element(rVenue_el, "netPmtPaidRecvMarketableLimitOrdersUsd", format_decimal2_or_nm(venue_data.net_pmt_paid_recv_marketable_limit_orders_usd))
            _add_element(rVenue_el, "netPmtPaidRecvMarketableLimitOrdersCph", format_cph4_or_nm(venue_data.net_pmt_paid_recv_marketable_limit_orders_cph))
            _add_element(rVenue_el, "netPmtPaidRecvNonMarketableLimitOrdersUsd", format_decimal2_or_nm(venue_data.net_pmt_paid_recv_non_marketable_limit_orders_usd))
            _add_element(rVenue_el, "netPmtPaidRecvNonMarketableLimitOrdersCph", format_cph4_or_nm(venue_data.net_pmt_paid_recv_non_marketable_limit_orders_cph))
            _add_element(rVenue_el, "netPmtPaidRecvOtherOrdersUsd", format_decimal2_or_nm(venue_data.net_pmt_paid_recv_other_orders_usd))
            _add_element(rVenue_el, "netPmtPaidRecvOtherOrdersCph", format_cph4_or_nm(venue_data.net_pmt_paid_recv_other_orders_cph))
            # Add materialAspects for this venue if present
            if venue_data.payment_disclosure_link: # Changed from material_aspects to payment_disclosure_link
                _add_element(rVenue_el, "materialAspects", venue_data.payment_disclosure_link)
            # Optional fields like mic, mpid, paymentDisclosureLink would be added here if available
            # _add_element(rVenue_el, "mic", venue_data.mic) # If present
            # _add_element(rVenue_el, "mpid", venue_data.mpid) # If present
            # _add_element(rVenue_el, "paymentDisclosureLink", venue_data.payment_disclosure_link) # If present

    # Handle s_directed_categories similarly if they exist and are needed for this report type
    # For 606(a)(1), usually only non-directed are detailed this way.

    # Old code for populating a different structure, now replaced by the loop above:
    # for month_data in quarterly_report_month_data.months: # This was for the old structure
    #     monthly_el = _add_element(root, "monData") # Example, adjust to XSD
    #     _add_element(monthly_el, "monthName", month_data.month_name)
    #     for category_data in month_data.categories:
    #         cat_el = _add_element(monthly_el, "category")
    #         _add_element(cat_el, "categoryName", category_data.category_name)
    #         for venue_data in category_data.venues:
    #             ven_el = _add_element(cat_el, "venue")
    #             _add_element(ven_el, "venueName", venue_data.venue_name)
    #             _add_element(ven_el, "ndoPct", venue_data.ndo_pct)
    #             _add_element(ven_el, "marketOrderPct", venue_data.market_order_pct)
    #             _add_element(ven_el, "marketableLimitOrderPct", venue_data.marketable_limit_order_pct)
    #             _add_element(ven_el, "nonMarketableLimitOrderPct", venue_data.non_marketable_limit_order_pct)
    #             _add_element(ven_el, "otherOrderPct", venue_data.other_order_pct)
    #             _add_element(ven_el, "avgNetExecRate", venue_data.avg_net_exec_rate)
    #             _add_element(ven_el, "avgExecSize", venue_data.avg_exec_size)
    #             _add_element(ven_el, "marketCenterFeeRate", venue_data.market_center_fee_rate)
    #             _add_element(ven_el, "netPmtPaidRecvMarketOrders", venue_data.net_pmt_paid_recv_market_orders)
    #             _add_element(ven_el, "netPmtPaidRecvMarketableLimitOrders", venue_data.net_pmt_paid_recv_marketable_limit_orders)
    #             _add_element(ven_el, "netPmtPaidRecvNonMarketableLimitOrders", venue_data.net_pmt_paid_recv_non_marketable_limit_orders)
    #             _add_element(ven_el, "netPmtPaidRecvOtherOrders", venue_data.net_pmt_paid_recv_other_orders)
    #             if venue_data.material_aspects: # Add material aspects if they exist
    #                 _add_element(ven_el, "materialAspects", venue_data.material_aspects)

    # 6. Write the XML to file
    tree = etree.ElementTree(root)
    tree.write(output_xml_filepath, pretty_print=True, xml_declaration=True, encoding='UTF-8')
    print(f"Successfully generated XML: {output_xml_filepath}")

    # 7. Validate the generated XML against the XSD
    is_valid, errors = validate_xml_against_xsd(output_xml_filepath, XSD_FILE_PATH)
    if is_valid:
        print("XML validation successful.")
    else:
        print("XML validation failed. Errors:")
        for err in errors:
            print(f"- {err}")

# --- New Wrapper Function for Module Usage ---
def perform_6151_conversion(excel_filepath, output_dir, firm_name, year, qtr):
    """
    Callable function to perform the 6151 conversion.
    Manages file paths and calls the core XML creation logic.
    Returns a tuple: (path_to_xml_file, validation_status, validation_errors).
    validation_status is True if valid, False otherwise.
    validation_errors is a list of error messages if invalid, or an empty list if valid.
    """
    print(f"Starting 6151 conversion for: {excel_filepath}")
    print(f"Output directory: {output_dir}")
    print(f"Firm: {firm_name}, Year: {year}, Quarter: {qtr}")

    # Default material aspects text - consider making this configurable if needed
    material_aspects_text = (
        "The Firm's order routing decisions are based on a variety of factors, including the size and type of order, "
        "the speed and likelihood of execution, the availability of price improvement, and the cost of execution. "
        "The Firm regularly reviews the execution quality obtained from different market centers and makes adjustments "
        "to its routing practices as necessary. Specific details regarding any payment for order flow arrangements "
        "or profit-sharing relationships are disclosed in the links provided for each venue."
    )

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Construct output XML filepath
    base_filename = os.path.splitext(os.path.basename(excel_filepath))[0]
    # A more robust way to name the output, incorporating firm, year, qtr
    # Example: FirmName_606_NMS_YYYY_QQ.xml
    # For now, let's stick to a simpler derivation and ensure it uses the provided params
    # Ensure CIK (if available and part of firm_name) or a sanitized firm_name is used
    sanitized_firm_name = "".join(c if c.isalnum() else "_" for c in firm_name.split(" ")[0]) # First word, alphanumeric
    output_xml_filename = f"{sanitized_firm_name}_606_NMS_{year}_Q{qtr}.xml"
    output_xml_filepath = os.path.join(output_dir, output_xml_filename)

    print(f"Output XML will be: {output_xml_filepath}")

    try:
        # Call the main XML creation function
        create_finra_6151_xml(
            excel_filepath=excel_filepath,
            output_xml_filepath=output_xml_filepath,
            firm_name=firm_name,
            reporting_year=str(year),
            reporting_quarter=str(qtr),
            material_aspects_text=material_aspects_text
        )
        print(f"Successfully generated XML: {output_xml_filepath}")

        # Validate the generated XML
        print(f"Validating '{output_xml_filepath}' against XSD: '{XSD_FILE_PATH}'")
        is_valid, errors = validate_xml_against_xsd(output_xml_filepath, XSD_FILE_PATH)

        return output_xml_filepath, is_valid, errors

    except Exception as e:
        print(f"Error during 6151 conversion process: {e}")
        # In case of an error during XML creation itself, we can't validate
        return None, False, [f"Error during XML creation: {e}"]

# --- Main execution --- 
def main():
    parser = argparse.ArgumentParser(description="Convert FINRA Order Handling Excel to XML.")
    parser.add_argument("excel_path", help="Path to the input Excel file.")
    parser.add_argument("output_dir", help="Directory to save the output XML file.")
    parser.add_argument("firm_name", help="Firm name (e.g., Example Firm).")
    parser.add_argument("year", help="Year (e.g., 2023).")
    parser.add_argument("qtr", help="Quarter (e.g., 1 for Q1).")
    args = parser.parse_args()

    print(f"Starting XML generation for Firm {args.firm_name}, Q{args.qtr} {args.year}.")
    print(f"Input Excel: {args.excel_path}")
    # Output path will be determined and printed within perform_6151_conversion or create_finra_6151_xml
    # For CLI, the perform_6151_conversion will print the output path via create_finra_6151_xml

    try:
        # Call the refactored conversion function
        output_xml_file, is_valid, errors = perform_6151_conversion(
            excel_filepath=args.excel_path,
            output_dir=args.output_dir,
            firm_name=args.firm_name, 
            year=args.year, # year and qtr are strings from argparse
            qtr=args.qtr
        )
        # The success message and validation output are handled within create_finra_6151_xml
    except Exception as e:
        print(f"An error occurred during 6151 conversion: {e}")

if __name__ == '__main__':
    main()
