import lxml.etree as etree
import datetime
from datetime import timezone # Added for timezone.utc
import os

# --- Helper functions for formatting based on XSD types ---
def format_pct(value):
    """Formats a number to PctType (string, 0.00-100.00, 2 decimal places)."""
    if value is None or value == "": # Simplified check for None or empty string
        return ""  
    try:
        num = float(value)
        return f"{num:.2f}"
    except ValueError:
        return "" 

def format_cph(value):
    """Formats a number to CphType (string, 4 decimal places)."""
    if value is None or value == "":
        return "" 
    try:
        num = float(value)
        return f"{num:.4f}"
    except ValueError:
        return ""

def format_usd(value):
    """Formats a number to USD (xs:decimal, typically 2 decimal places for currency)."""
    if value is None or value == "":
        return "0.00" 
    try:
        num = float(value)
        return f"{num:.2f}"
    except ValueError:
        return "0.00"

# --- Data Classes to Mirror XSD Structure --- 
class VenueData:
    def __init__(self, venue_name, order_pct, market_pct, 
                 marketable_limit_pct, non_marketable_limit_pct, other_orders_pct,
                 net_pmt_market_usd, net_pmt_market_cph, 
                 net_pmt_marketable_limit_usd, net_pmt_marketable_limit_cph,
                 net_pmt_non_marketable_limit_usd, net_pmt_non_marketable_limit_cph,
                 net_pmt_other_usd, net_pmt_other_cph, mic=None, material_aspects=""):
        self.venue_name = venue_name
        self.mic = mic
        self.order_pct = order_pct 
        self.market_pct = market_pct
        self.marketable_limit_pct = marketable_limit_pct
        self.non_marketable_limit_pct = non_marketable_limit_pct
        self.other_orders_pct = other_orders_pct
        self.net_pmt_market_usd = net_pmt_market_usd
        self.net_pmt_market_cph = net_pmt_market_cph
        self.net_pmt_marketable_limit_usd = net_pmt_marketable_limit_usd
        self.net_pmt_marketable_limit_cph = net_pmt_marketable_limit_cph
        self.net_pmt_non_marketable_limit_usd = net_pmt_non_marketable_limit_usd
        self.net_pmt_non_marketable_limit_cph = net_pmt_non_marketable_limit_cph
        self.net_pmt_other_usd = net_pmt_other_usd
        self.net_pmt_other_cph = net_pmt_other_cph
        self.material_aspects = material_aspects 

class SecurityCategoryData:
    """Holds data for rSP500, rOtherStocks, or rOptions sections."""
    def __init__(self, category_xml_tag_name):
        self.category_xml_tag_name = category_xml_tag_name
        self.ndo_pct = 0.0
        self.ndo_market_pct = 0.0
        self.ndo_marketable_limit_pct = 0.0
        self.ndo_non_marketable_limit_pct = 0.0
        self.ndo_other_pct = 0.0
        self.venues = [] # List of VenueData objects

class MonthlyData: 
    """Holds data for one <rMonthly> element for a specific month."""
    def __init__(self, month_num_str): 
        self.month_num_str = month_num_str 
        self.sp500_data = SecurityCategoryData("rSP500")
        self.other_stocks_data = SecurityCategoryData("rOtherStocks")
        self.options_data = SecurityCategoryData("rOptions")

class R606ReportData: 
    """Holds all data for the <r606> report."""
    def __init__(self, bd_name, report_year, report_quarter_num_str, report_version="1.0"):
        self.version = report_version 
        self.bd_name = str(bd_name) 
        self.year = str(report_year) 
        self.qtr = str(report_quarter_num_str) 
        self.timestamp = datetime.datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        self.monthly_data_list = [] # List of MonthlyData objects

# --- XML Element Creation Helper ---
def _add_element(parent, tag_name, text_content=None):
    element = etree.SubElement(parent, tag_name)
    if text_content is not None:
        element.text = str(text_content)
    return element

# --- PDF Parsing Function (Placeholder) ---
def parse_pdf_data(pdf_filepath, reporting_year, reporting_quarter):
    """
    Parses the PDF file and returns a list of three populated MonthlyData objects.
    This is a STUB and needs full implementation with a PDF parsing library.
    It should also handle extraction/assignment of material_aspects per venue.
    """
    print(f"STUB: Attempting to parse PDF data from {pdf_filepath} for Y{reporting_year} Q{reporting_quarter}")
    
    all_monthly_data = []
    quarter_months_map = {
        1: [1, 2, 3], 2: [4, 5, 6], 3: [7, 8, 9], 4: [10, 11, 12]
    }
    months_in_quarter = quarter_months_map.get(reporting_quarter)
    if not months_in_quarter:
        raise ValueError(f"Invalid reporting quarter: {reporting_quarter}")

    # Placeholder: Create dummy data for each month
    for month_num in months_in_quarter:
        month_str = f"{month_num:02d}"
        monthly_item = MonthlyData(month_str)
        
        # Dummy S&P 500 data
        monthly_item.sp500_data.ndo_pct = 75.0
        monthly_item.sp500_data.venues.append(
            VenueData("NYSE_FROM_PDF", 50.0, 20.0, 10.0, 10.0, 10.0, 
                      100.0, 0.001, 50.0, 0.0005, 20.0, 0.0002, 10.0, 0.0001, 
                      mic="XNYS", material_aspects="MA for NYSE from PDF placeholder")
        )
        # Dummy Other Stocks data
        monthly_item.other_stocks_data.ndo_pct = 80.0
        monthly_item.other_stocks_data.venues.append(
            VenueData("NASDAQ_FROM_PDF", 60.0, 25.0, 15.0, 10.0, 10.0, 
                      120.0, 0.0012, 60.0, 0.0006, 25.0, 0.0003, 15.0, 0.0001, 
                      mic="XNAS", material_aspects="MA for NASDAQ from PDF placeholder")
        )
        # Dummy Options data (often less detailed or N/A for some firms)
        monthly_item.options_data.ndo_pct = 0.0 # Example: no options NDO

        all_monthly_data.append(monthly_item)
        
    print(f"STUB: parse_pdf_data returning {len(all_monthly_data)} MonthlyData objects with placeholder values.")
    return all_monthly_data

# --- XML Tree Building Function ---
def build_r606_xml_tree(report_data_obj):
    """Builds the lxml.etree.ElementTree from an R606ReportData object."""
    root_attributes = {
        "version": report_data_obj.version,
        "bd": report_data_obj.bd_name,
        "year": report_data_obj.year,
        "qtr": report_data_obj.qtr
    }
    root = etree.Element("r606", attrib=root_attributes)
    
    _add_element(root, "timestamp", report_data_obj.timestamp)

    for month_report_item in report_data_obj.monthly_data_list:
        r_monthly_elem = _add_element(root, "rMonthly")
        _add_element(r_monthly_elem, "mon", month_report_item.month_num_str)

        for sec_cat_data in [month_report_item.sp500_data, month_report_item.other_stocks_data, month_report_item.options_data]:
            sec_cat_elem = _add_element(r_monthly_elem, sec_cat_data.category_xml_tag_name)
            
            _add_element(sec_cat_elem, "ndoPct", format_pct(sec_cat_data.ndo_pct))
            _add_element(sec_cat_elem, "ndoMarketPct", format_pct(sec_cat_data.ndo_market_pct))
            _add_element(sec_cat_elem, "ndoMarketableLimitPct", format_pct(sec_cat_data.ndo_marketable_limit_pct))
            _add_element(sec_cat_elem, "ndoNonmarketableLimitPct", format_pct(sec_cat_data.ndo_non_marketable_limit_pct))
            _add_element(sec_cat_elem, "ndoOtherPct", format_pct(sec_cat_data.ndo_other_pct))
            
            r_venues_elem = _add_element(sec_cat_elem, "rVenues")
            for venue in sec_cat_data.venues:
                r_venue_elem = _add_element(r_venues_elem, "rVenue")
                
                if venue.mic: 
                    _add_element(r_venue_elem, "mic", venue.mic)
                elif venue.venue_name:
                    _add_element(r_venue_elem, "name", venue.venue_name)
                else:
                    _add_element(r_venue_elem, "name", "UNKNOWN_VENUE") 
                
                _add_element(r_venue_elem, "orderPct", format_pct(venue.order_pct))
                _add_element(r_venue_elem, "marketPct", format_pct(venue.market_pct))
                _add_element(r_venue_elem, "marketableLimitPct", format_pct(venue.marketable_limit_pct))
                _add_element(r_venue_elem, "nonMarketableLimitPct", format_pct(venue.non_marketable_limit_pct))
                _add_element(r_venue_elem, "otherPct", format_pct(venue.other_orders_pct))
                
                _add_element(r_venue_elem, "netPmtPaidRecvMarketOrdersUsd", format_usd(venue.net_pmt_market_usd))
                _add_element(r_venue_elem, "netPmtPaidRecvMarketOrdersCph", format_cph(venue.net_pmt_market_cph))
                _add_element(r_venue_elem, "netPmtPaidRecvMarketableLimitOrdersUsd", format_usd(venue.net_pmt_marketable_limit_usd))
                _add_element(r_venue_elem, "netPmtPaidRecvMarketableLimitOrdersCph", format_cph(venue.net_pmt_marketable_limit_cph))
                _add_element(r_venue_elem, "netPmtPaidRecvNonMarketableLimitOrdersUsd", format_usd(venue.net_pmt_non_marketable_limit_usd))
                _add_element(r_venue_elem, "netPmtPaidRecvNonMarketableLimitOrdersCph", format_cph(venue.net_pmt_non_marketable_limit_cph))
                _add_element(r_venue_elem, "netPmtPaidRecvOtherOrdersUsd", format_usd(venue.net_pmt_other_usd))
                _add_element(r_venue_elem, "netPmtPaidRecvOtherOrdersCph", format_cph(venue.net_pmt_other_cph))
                
                _add_element(r_venue_elem, "materialAspects", venue.material_aspects) 

    return etree.ElementTree(root)

# --- Main Orchestration Function ---
def main_pdf_to_xml_conversion(pdf_filepath, output_xml_filepath, 
                               firm_crd, reporting_year, reporting_quarter, 
                               schema_version="1.0"):
    """Orchestrates the PDF to XML conversion process."""
    print(f"Starting PDF to XML conversion for: {pdf_filepath}")
    try:
        # 1. Parse PDF data (currently a stub)
        # This function should return a list of three fully populated MonthlyData objects.
        monthly_data_from_pdf = parse_pdf_data(pdf_filepath, reporting_year, reporting_quarter)

        # 2. Prepare the main report data object
        report_obj = R606ReportData(
            bd_name=firm_crd,
            report_year=reporting_year,
            report_quarter_num_str=str(reporting_quarter),
            report_version=schema_version
        )
        report_obj.monthly_data_list = monthly_data_from_pdf

        # 3. Build the XML tree
        xml_tree = build_r606_xml_tree(report_obj)

        # 4. Write XML to file
        os.makedirs(os.path.dirname(output_xml_filepath), exist_ok=True)
        xml_tree.write(output_xml_filepath, pretty_print=True, xml_declaration=True, encoding='UTF-8')
        print(f"Successfully generated XML: {output_xml_filepath}")
        return output_xml_filepath

    except ValueError as ve:
        print(f"Configuration Error: {ve}")
    except Exception as e:
        print(f"An error occurred during PDF to XML conversion: {e}")
        # import traceback
        # traceback.print_exc() # For more detailed debugging if needed
    return None

if __name__ == '__main__':
    print("Running PDF to 606 XML Converter (with STUB PDF parsing)...")
    # --- Configuration for a sample run ---
    sample_pdf_file = "/path/to/your/sample_report.pdf" # Replace with an actual PDF path if testing parse_pdf_data later
    output_directory = "/Users/stuartkerr/Library/CloudStorage/OneDrive-Personal/Code/EXCEL TO EDGAR XML/Output_PDF_Converted"
    
    # These would typically come from user input or a batch processing script
    target_firm_crd = "12345" # Example CRD
    target_year = 2025
    target_quarter = 1 # 1 for Q1, 2 for Q2, etc.

    # Construct output filename
    output_filename = f"{target_firm_crd}_606_NMS_{target_year}_Q{target_quarter}_from_pdf.xml"
    full_output_path = os.path.join(output_directory, output_filename)

    # Create a dummy PDF file for the script to 'process' (since parsing is a stub)
    # In a real scenario, sample_pdf_file should exist.
    # For this test, we just need the main_pdf_to_xml_conversion to run with the stub.
    print(f"Note: PDF parsing is currently a STUB. '{sample_pdf_file}' doesn't need to exist for this initial test.")

    generated_file = main_pdf_to_xml_conversion(
        pdf_filepath=sample_pdf_file, 
        output_xml_filepath=full_output_path,
        firm_crd=target_firm_crd,
        reporting_year=target_year,
        reporting_quarter=target_quarter
    )

    if generated_file:
        print(f"\nSUCCESS: XML file generated at: {generated_file}")
        print("Please check the file content. Remember that PDF data is currently placeholder.")
    else:
        print("\nFAILURE: XML file generation failed. Check logs above.")

    # Example of how you might run for another quarter
    # target_quarter_q2 = 2
    # output_filename_q2 = f"{target_firm_crd}_606_NMS_{target_year}_Q{target_quarter_q2}_from_pdf.xml"
    # full_output_path_q2 = os.path.join(output_directory, output_filename_q2)
    # main_pdf_to_xml_conversion(
    #     pdf_filepath=sample_pdf_file, 
    #     output_xml_filepath=full_output_path_q2,
    #     firm_crd=target_firm_crd,
    #     reporting_year=target_year,
    #     reporting_quarter=target_quarter_q2
    # )
