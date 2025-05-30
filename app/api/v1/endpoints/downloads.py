from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import StreamingResponse
from datetime import date
import io
import json
import csv

from libs.http_client import HTTPXClient
from app.core.config import settings

router = APIRouter(prefix="/downloads", tags=["downloads"])


@router.get("/csv")
async def download_csv(
    start_date: date = Query(
        ..., description="Start date (YYYY-MM-DD)", alias="startDate"
    ),
    end_date: date = Query(..., description="End date (YYYY-MM-DD)", alias="endDate"),
    limit: int = Query(
        default=100, ge=1, le=5000, description="Number of records to fetch"
    ),
):
    """
    Download FDA device event data as CSV file.

    Args:
        start_date: Start date for data filtering
        end_date: End date for data filtering
        limit: Maximum number of records to return (1-5000)

    Returns:
        CSV file as downloadable response
    """

    # Format dates for FDA API (they expect YYYY-MM-DD format)
    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")

    # Construct FDA API URL with query parameters
    fda_url = (
        f"{settings.FDA_BASE_URL}"
        f"?limit={limit}"
        f"&search=device.device_report_product_code:FKX+AND+date_received:[{start_date_str}+TO+{end_date_str}]"
    )

    try:
        # Fetch data from FDA API
        http_client = HTTPXClient()
        response = await http_client.async_get(fda_url)

        # Parse JSON response
        if isinstance(response, str):
            data = json.loads(response)
        else:
            data = response

        # Check if response has results
        if "results" not in data or not data["results"]:
            raise HTTPException(
                status_code=404, detail="No data found for the specified date range"
            )

        # Convert JSON data to CSV
        csv_content = await json_to_csv(data["results"])

        # Create filename with date range
        filename = f"fda_raw_data_{start_date_str}_to_{end_date_str}.csv"

        # Return CSV as downloadable file
        return StreamingResponse(
            io.StringIO(csv_content),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )

    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500, detail="Invalid JSON response from FDA API"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error processing request: {str(e)}"
        )


async def json_to_csv(json_data: list) -> str:
    """
    Convert JSON data to CSV format with specific fields only.

    Args:
        json_data: List of dictionaries containing FDA device event data

    Returns:
        CSV content as string
    """
    if not json_data:
        return ""

    # Create CSV in memory
    output = io.StringIO()

    # Extract specific fields from each record
    extracted_data = []
    for item in json_data:
        extracted_item = extract_specific_fields(item)
        extracted_data.append(extracted_item)

    if extracted_data:
        # Define the exact field order we want
        fieldnames = [
            "Web Address",
            "Report Number",
            "Event Date",
            "Event Type",
            "Manufacturer",
            "Date Received",
            "Product Code",
            "Brand Name",
            "Device Problem",
            "Patient Problem",
            "PMA/PMN Number",
            "Exemption Number",
            "Number of Events",
            "Event Text",
        ]

        # Write CSV
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(extracted_data)

    csv_content = output.getvalue()
    output.close()

    return csv_content


def extract_specific_fields(record: dict) -> dict:
    """
    Extract only the specific fields we need from FDA device event record.

    Args:
        record: Single FDA device event record

    Returns:
        Dictionary with only the required fields
    """
    from datetime import datetime

    # Helper function to format date
    def format_date(date_str: str) -> str:
        if not date_str or date_str == "":
            return ""
        try:
            # FDA dates are in YYYYMMDD format
            if len(date_str) == 8:
                date_obj = datetime.strptime(date_str, "%Y%m%d")
                return date_obj.strftime("%m-%d-%Y %H:%M:%S")
            return date_str
        except (ValueError, TypeError):
            return date_str

    # Helper function to safely get nested values
    def safe_get(data, *keys, default=""):
        for key in keys:
            if isinstance(data, dict) and key in data:
                data = data[key]
            elif isinstance(data, list) and len(data) > 0:
                data = data[0]  # Take first item from list
                if isinstance(data, dict) and key in data:
                    data = data[key]
                else:
                    return default
            else:
                return default
        return data if data is not None else default

    # Extract mdr_report_key for web address
    mdr_report_key = record.get("mdr_report_key", "")
    product_code = safe_get(record, "device", "device_report_product_code")

    # Construct web address
    web_address = ""
    if mdr_report_key and product_code:
        web_address = f"https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfMAUDE/Detail.CFM?MDRFOI__ID={mdr_report_key}&pc={product_code}"

    # Extract event text (combine Description and Manufacturer Narrative)
    event_text = extract_event_text(record.get("mdr_text", []))

    # Extract device problems
    device_problems = record.get("product_problems", [])
    device_problem_str = ", ".join(device_problems) if device_problems else ""

    # Extract patient problems
    patient_problems = []
    patients = record.get("patient", [])
    if patients:
        for patient in patients:
            if "patient_problems" in patient:
                patient_problems.extend(patient["patient_problems"])
    patient_problem_str = ", ".join(set(patient_problems)) if patient_problems else ""

    return {
        "Web Address": web_address,
        "Report Number": record.get("report_number", ""),
        "Event Date": format_date(record.get("date_of_event", "")),
        "Event Type": record.get("event_type", ""),
        "Manufacturer": safe_get(record, "device", "manufacturer_d_name"),
        "Date Received": format_date(record.get("date_received", "")),
        "Product Code": product_code,
        "Brand Name": safe_get(record, "device", "brand_name"),
        "Device Problem": device_problem_str,
        "Patient Problem": patient_problem_str,
        "PMA/PMN Number": record.get("pma_pmn_number", ""),
        "Exemption Number": record.get("exemption_number", ""),
        "Number of Events": "1",  # Each record represents one event
        "Event Text": event_text,
    }


def extract_event_text(mdr_text_list: list) -> str:
    """
    Extract and combine event description and manufacturer narrative from MDR text entries.
    Ensures only the first unique 'Description of Event or Problem' is included,
    while all 'Additional Manufacturer Narrative' entries are concatenated.

    Args:
        mdr_text_list: List of MDR text entries

    Returns:
        Combined event text string
    """
    event_description = ""
    manufacturer_narratives = []  # List to collect all narratives
    seen_descriptions = set()  # Set to track unique descriptions

    # Process each text entry
    for text_entry in mdr_text_list:
        text_type = text_entry.get("text_type_code", "")
        text_content = text_entry.get("text", "").strip()

        if text_type == "Description of Event or Problem" and text_content:
            # Add only if not seen before
            if text_content not in seen_descriptions:
                event_description = text_content
                seen_descriptions.add(text_content)
        elif text_type == "Additional Manufacturer Narrative" and text_content:
            # Collect all narratives
            manufacturer_narratives.append(text_content)

    # Build the combined text
    combined_text = ""
    if event_description:
        combined_text += f"Event Description: {event_description}"
    if manufacturer_narratives:
        # Join all narratives with a space
        narrative_text = " ".join(manufacturer_narratives)
        if combined_text:
            combined_text += f" Manufacturer Narrative: {narrative_text}"
        else:
            combined_text = f"Manufacturer Narrative: {narrative_text}"

    return combined_text


# Alternative endpoint that returns JSON (for testing/debugging)
@router.get("/json")
async def get_json_data(
    start_date: date = Query(
        ..., description="Start date (YYYY-MM-DD)", alias="startDate"
    ),
    end_date: date = Query(..., description="End date (YYYY-MM-DD)", alias="endDate"),
    limit: int = Query(
        default=100, ge=1, le=5000, description="Number of records to fetch"
    ),
):
    """
    Get FDA device event data as JSON (for testing purposes).
    """
    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")

    fda_url = (
        f"{settings.FDA_BASE_URL}"
        f"?limit={limit}"
        f"&search=device.device_report_product_code:FKX+AND+date_received:[{start_date_str}+TO+{end_date_str}]"
    )

    try:
        http_client = HTTPXClient()
        response = await http_client.async_get(fda_url)

        if isinstance(response, str):
            return json.loads(response)
        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching data: {str(e)}")
