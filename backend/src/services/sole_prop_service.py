"""
Sole Proprietorship Service — handles registration guidance for sole proprietors.

Unlike companies and LLPs, sole proprietorships do not require MCA registration.
The primary registrations are:
1. GST Registration (mandatory if turnover > Rs 40 Lakh / Rs 20 Lakh for services)
2. MSME / Udyam Registration
3. Shop & Establishment Act license (state-specific)
"""

import logging
from typing import Optional, Dict, Any, List
from datetime import date

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# State-wise Shop & Establishment Act guidance
# ---------------------------------------------------------------------------

SHOP_ACT_GUIDANCE: Dict[str, Dict[str, Any]] = {
    "Maharashtra": {
        "act_name": "Maharashtra Shops and Establishments (Regulation of Employment and Conditions of Service) Act, 2017",
        "authority": "Local Municipal Corporation / Council",
        "portal": "https://aaplesarkar.mahaonline.gov.in",
        "fee_range": "Rs 200 - Rs 5,000 (varies by area and number of employees)",
        "validity": "Permanent (with annual renewal for some municipalities)",
        "timeline": "7-15 working days",
        "documents_required": [
            "PAN Card of proprietor",
            "Aadhaar Card of proprietor",
            "Proof of business premises (rent agreement / ownership proof)",
            "Passport-size photograph",
            "NOC from landlord (if rented)",
        ],
        "key_provisions": [
            "Registration mandatory within 30 days of commencement",
            "Working hours: 9 hours/day, 48 hours/week",
            "Weekly holiday mandatory",
            "Must display registration certificate at premises",
        ],
    },
    "Delhi": {
        "act_name": "Delhi Shops and Establishments Act, 1954",
        "authority": "District Labour Commissioner",
        "portal": "https://labour.delhi.gov.in",
        "fee_range": "Rs 100 - Rs 500",
        "validity": "3 years (renewable)",
        "timeline": "7-10 working days",
        "documents_required": [
            "PAN Card of proprietor",
            "Aadhaar Card of proprietor",
            "Proof of business premises",
            "Passport-size photograph",
            "Affidavit on stamp paper",
        ],
        "key_provisions": [
            "Registration mandatory within 30 days of commencement",
            "Working hours: 9 hours/day, 48 hours/week",
            "Opening hours: 9:00 AM, Closing hours: 9:00 PM (extendable)",
            "Spread-over not to exceed 10.5 hours",
        ],
    },
    "Karnataka": {
        "act_name": "Karnataka Shops and Commercial Establishments Act, 1961",
        "authority": "Labour Department, Karnataka",
        "portal": "https://labour.karnataka.gov.in",
        "fee_range": "Rs 250 - Rs 2,500",
        "validity": "5 years (renewable)",
        "timeline": "7-15 working days",
        "documents_required": [
            "PAN Card of proprietor",
            "Aadhaar Card of proprietor",
            "Proof of business premises",
            "Passport-size photograph",
            "Trade license (if applicable)",
        ],
        "key_provisions": [
            "Registration mandatory for all shops and commercial establishments",
            "Working hours: 9 hours/day, 48 hours/week",
            "One paid holiday per week",
            "Annual leave of 15 days after completing one year",
        ],
    },
    "Tamil Nadu": {
        "act_name": "Tamil Nadu Shops and Establishments Act, 1947",
        "authority": "Inspector of Labour, Tamil Nadu",
        "portal": "https://labour.tn.gov.in",
        "fee_range": "Rs 300 - Rs 3,000",
        "validity": "5 years (renewable)",
        "timeline": "10-15 working days",
        "documents_required": [
            "PAN Card of proprietor",
            "Aadhaar Card of proprietor",
            "Proof of business premises",
            "Passport-size photograph",
        ],
        "key_provisions": [
            "Registration mandatory within 30 days",
            "Working hours: 8 hours/day, 48 hours/week",
            "Weekly holiday mandatory",
            "Overtime wages at double the ordinary rate",
        ],
    },
    "Telangana": {
        "act_name": "Telangana Shops and Establishments Act, 1988",
        "authority": "Commissioner of Labour, Telangana",
        "portal": "https://labour.telangana.gov.in",
        "fee_range": "Rs 200 - Rs 2,000",
        "validity": "5 years (renewable)",
        "timeline": "7-14 working days",
        "documents_required": [
            "PAN Card of proprietor",
            "Aadhaar Card of proprietor",
            "Proof of business premises",
            "Passport-size photograph",
        ],
        "key_provisions": [
            "Registration mandatory within 30 days",
            "Working hours: 9 hours/day, 48 hours/week",
            "Weekly holiday on Sunday",
        ],
    },
    "Gujarat": {
        "act_name": "Gujarat Shops and Establishments Act, 1948",
        "authority": "Inspector under the Act / Labour Department",
        "portal": "https://labour.gujarat.gov.in",
        "fee_range": "Rs 150 - Rs 1,500",
        "validity": "Permanent (annual filing)",
        "timeline": "7-10 working days",
        "documents_required": [
            "PAN Card of proprietor",
            "Aadhaar Card of proprietor",
            "Proof of business premises",
            "Passport-size photograph",
        ],
        "key_provisions": [
            "Registration mandatory within 30 days",
            "Working hours: 9 hours/day, 48 hours/week",
            "Weekly closed day mandatory",
        ],
    },
    "Uttar Pradesh": {
        "act_name": "Uttar Pradesh Dookan Aur Vanijya Adhishthan Adhiniyam, 1962",
        "authority": "Inspector of Shops / Labour Department",
        "portal": "https://uplabour.gov.in",
        "fee_range": "Rs 100 - Rs 1,000",
        "validity": "5 years (renewable)",
        "timeline": "15-30 working days",
        "documents_required": [
            "PAN Card of proprietor",
            "Aadhaar Card of proprietor",
            "Proof of business premises",
            "Passport-size photograph",
            "Affidavit on stamp paper",
        ],
        "key_provisions": [
            "Registration mandatory for all commercial establishments",
            "Working hours: 9 hours/day, 54 hours/week",
            "Weekly closed day",
        ],
    },
    "West Bengal": {
        "act_name": "West Bengal Shops and Establishments Act, 1963",
        "authority": "Labour Department, West Bengal",
        "portal": "https://wblc.gov.in",
        "fee_range": "Rs 150 - Rs 2,000",
        "validity": "3 years (renewable)",
        "timeline": "10-20 working days",
        "documents_required": [
            "PAN Card of proprietor",
            "Aadhaar Card of proprietor",
            "Proof of business premises",
            "Trade license from municipality",
        ],
        "key_provisions": [
            "Registration mandatory within 30 days",
            "Working hours: 8 hours/day, 48 hours/week",
            "Weekly holiday mandatory",
        ],
    },
    "Rajasthan": {
        "act_name": "Rajasthan Shops and Commercial Establishments Act, 1958",
        "authority": "Labour Department, Rajasthan",
        "portal": "https://labour.rajasthan.gov.in",
        "fee_range": "Rs 100 - Rs 1,500",
        "validity": "5 years (renewable)",
        "timeline": "7-15 working days",
        "documents_required": [
            "PAN Card of proprietor",
            "Aadhaar Card of proprietor",
            "Proof of business premises",
            "Passport-size photograph",
        ],
        "key_provisions": [
            "Registration mandatory within 30 days",
            "Working hours: 9 hours/day, 48 hours/week",
            "Weekly holiday",
        ],
    },
    "Madhya Pradesh": {
        "act_name": "Madhya Pradesh Shops and Establishments Act, 1958",
        "authority": "Chief Inspector of Shops and Establishments",
        "portal": "https://labour.mp.gov.in",
        "fee_range": "Rs 100 - Rs 1,000",
        "validity": "3 years (renewable)",
        "timeline": "10-15 working days",
        "documents_required": [
            "PAN Card of proprietor",
            "Aadhaar Card of proprietor",
            "Proof of business premises",
            "Passport-size photograph",
        ],
        "key_provisions": [
            "Registration mandatory within 30 days",
            "Working hours: 9 hours/day, 48 hours/week",
        ],
    },
    "Kerala": {
        "act_name": "Kerala Shops and Commercial Establishments Act, 1960",
        "authority": "Inspector of Shops / Labour Department",
        "portal": "https://labour.kerala.gov.in",
        "fee_range": "Rs 200 - Rs 2,500",
        "validity": "5 years (renewable)",
        "timeline": "7-15 working days",
        "documents_required": [
            "PAN Card of proprietor",
            "Aadhaar Card of proprietor",
            "Proof of business premises",
            "Passport-size photograph",
        ],
        "key_provisions": [
            "Registration mandatory within 30 days",
            "Working hours: 8 hours/day, 48 hours/week",
            "Weekly holiday mandatory",
            "Overtime at double the rate",
        ],
    },
    "Punjab": {
        "act_name": "Punjab Shops and Commercial Establishments Act, 1958",
        "authority": "Labour Department, Punjab",
        "portal": "https://pblabour.gov.in",
        "fee_range": "Rs 100 - Rs 1,000",
        "validity": "3 years (renewable)",
        "timeline": "10-15 working days",
        "documents_required": [
            "PAN Card of proprietor",
            "Aadhaar Card of proprietor",
            "Proof of business premises",
            "Passport-size photograph",
        ],
        "key_provisions": [
            "Registration mandatory within 30 days",
            "Working hours: 9 hours/day, 48 hours/week",
        ],
    },
    "Haryana": {
        "act_name": "Haryana Shops and Commercial Establishments Act, 1958",
        "authority": "Labour Department, Haryana",
        "portal": "https://hrylabour.gov.in",
        "fee_range": "Rs 100 - Rs 1,000",
        "validity": "3 years (renewable)",
        "timeline": "7-14 working days",
        "documents_required": [
            "PAN Card of proprietor",
            "Aadhaar Card of proprietor",
            "Proof of business premises",
        ],
        "key_provisions": [
            "Registration mandatory within 30 days",
            "Working hours: 9 hours/day, 48 hours/week",
        ],
    },
    "Bihar": {
        "act_name": "Bihar Shops and Establishments Act, 1953",
        "authority": "Labour Department, Bihar",
        "portal": "https://labour.bihar.gov.in",
        "fee_range": "Rs 100 - Rs 500",
        "validity": "3 years (renewable)",
        "timeline": "15-30 working days",
        "documents_required": [
            "PAN Card of proprietor",
            "Aadhaar Card of proprietor",
            "Proof of business premises",
        ],
        "key_provisions": [
            "Registration mandatory within 30 days",
            "Working hours as prescribed by the state",
        ],
    },
    "Odisha": {
        "act_name": "Odisha Shops and Commercial Establishments Act, 1956",
        "authority": "Labour Department, Odisha",
        "portal": "https://labdirodisha.gov.in",
        "fee_range": "Rs 100 - Rs 1,000",
        "validity": "3 years (renewable)",
        "timeline": "10-20 working days",
        "documents_required": [
            "PAN Card of proprietor",
            "Aadhaar Card of proprietor",
            "Proof of business premises",
        ],
        "key_provisions": [
            "Registration mandatory within 30 days",
            "Working hours: 9 hours/day, 48 hours/week",
        ],
    },
    "Jharkhand": {
        "act_name": "Jharkhand Shops and Establishments Act, 1953",
        "authority": "Labour Department, Jharkhand",
        "portal": "https://shramadhan.jharkhand.gov.in",
        "fee_range": "Rs 100 - Rs 500",
        "validity": "3 years (renewable)",
        "timeline": "15-30 working days",
        "documents_required": [
            "PAN Card of proprietor",
            "Aadhaar Card of proprietor",
            "Proof of business premises",
        ],
        "key_provisions": [
            "Registration mandatory within 30 days",
        ],
    },
    "Assam": {
        "act_name": "Assam Shops and Establishments Act, 1971",
        "authority": "Labour Department, Assam",
        "portal": "https://labour.assam.gov.in",
        "fee_range": "Rs 100 - Rs 1,000",
        "validity": "3 years (renewable)",
        "timeline": "15-20 working days",
        "documents_required": [
            "PAN Card of proprietor",
            "Aadhaar Card of proprietor",
            "Proof of business premises",
        ],
        "key_provisions": [
            "Registration mandatory within 30 days",
        ],
    },
    "Chhattisgarh": {
        "act_name": "Chhattisgarh Shops and Establishments Act, 1958",
        "authority": "Labour Department, Chhattisgarh",
        "portal": "https://cglabour.nic.in",
        "fee_range": "Rs 100 - Rs 1,000",
        "validity": "3 years (renewable)",
        "timeline": "10-15 working days",
        "documents_required": [
            "PAN Card of proprietor",
            "Aadhaar Card of proprietor",
            "Proof of business premises",
        ],
        "key_provisions": [
            "Registration mandatory within 30 days",
        ],
    },
    "Goa": {
        "act_name": "Goa Shops and Establishments Act, 1973",
        "authority": "Labour Commissioner, Goa",
        "portal": "https://www.goa.gov.in",
        "fee_range": "Rs 200 - Rs 1,500",
        "validity": "5 years (renewable)",
        "timeline": "7-14 working days",
        "documents_required": [
            "PAN Card of proprietor",
            "Aadhaar Card of proprietor",
            "Proof of business premises",
        ],
        "key_provisions": [
            "Registration mandatory within 30 days",
        ],
    },
    "Himachal Pradesh": {
        "act_name": "Himachal Pradesh Shops and Commercial Establishments Act, 1969",
        "authority": "Labour Department, Himachal Pradesh",
        "portal": "https://himachal.nic.in",
        "fee_range": "Rs 100 - Rs 500",
        "validity": "3 years (renewable)",
        "timeline": "10-15 working days",
        "documents_required": [
            "PAN Card of proprietor",
            "Aadhaar Card of proprietor",
            "Proof of business premises",
        ],
        "key_provisions": [
            "Registration mandatory within 30 days",
        ],
    },
    "Uttarakhand": {
        "act_name": "Uttarakhand Shops and Commercial Establishments Act, 1962",
        "authority": "Labour Department, Uttarakhand",
        "portal": "https://labour.uk.gov.in",
        "fee_range": "Rs 100 - Rs 500",
        "validity": "3 years (renewable)",
        "timeline": "10-15 working days",
        "documents_required": [
            "PAN Card of proprietor",
            "Aadhaar Card of proprietor",
            "Proof of business premises",
        ],
        "key_provisions": [
            "Registration mandatory within 30 days",
        ],
    },
    "Andhra Pradesh": {
        "act_name": "Andhra Pradesh Shops and Establishments Act, 1988",
        "authority": "Commissioner of Labour, Andhra Pradesh",
        "portal": "https://labour.ap.gov.in",
        "fee_range": "Rs 200 - Rs 2,000",
        "validity": "5 years (renewable)",
        "timeline": "7-14 working days",
        "documents_required": [
            "PAN Card of proprietor",
            "Aadhaar Card of proprietor",
            "Proof of business premises",
            "Passport-size photograph",
        ],
        "key_provisions": [
            "Registration mandatory within 30 days",
            "Working hours: 9 hours/day, 48 hours/week",
        ],
    },
    "Arunachal Pradesh": {
        "act_name": "Arunachal Pradesh Shops and Establishments Act",
        "authority": "Labour Department, Arunachal Pradesh",
        "portal": "https://arunachalpradesh.gov.in",
        "fee_range": "Rs 100 - Rs 500",
        "validity": "3 years (renewable)",
        "timeline": "15-30 working days",
        "documents_required": [
            "PAN Card of proprietor",
            "Aadhaar Card of proprietor",
            "Proof of business premises",
        ],
        "key_provisions": ["Registration mandatory within 30 days"],
    },
    "Manipur": {
        "act_name": "Manipur Shops and Establishments Act, 1972",
        "authority": "Labour Department, Manipur",
        "portal": "https://manipur.gov.in",
        "fee_range": "Rs 100 - Rs 500",
        "validity": "3 years (renewable)",
        "timeline": "15-30 working days",
        "documents_required": [
            "PAN Card of proprietor",
            "Aadhaar Card of proprietor",
            "Proof of business premises",
        ],
        "key_provisions": ["Registration mandatory within 30 days"],
    },
    "Meghalaya": {
        "act_name": "Meghalaya Shops and Establishments Act",
        "authority": "Labour Department, Meghalaya",
        "portal": "https://meghalaya.gov.in",
        "fee_range": "Rs 100 - Rs 500",
        "validity": "3 years (renewable)",
        "timeline": "15-30 working days",
        "documents_required": [
            "PAN Card of proprietor",
            "Aadhaar Card of proprietor",
            "Proof of business premises",
        ],
        "key_provisions": ["Registration mandatory within 30 days"],
    },
    "Mizoram": {
        "act_name": "Mizoram Shops and Establishments Act",
        "authority": "Labour Department, Mizoram",
        "portal": "https://mizoram.gov.in",
        "fee_range": "Rs 100 - Rs 500",
        "validity": "3 years (renewable)",
        "timeline": "15-30 working days",
        "documents_required": [
            "PAN Card of proprietor",
            "Aadhaar Card of proprietor",
            "Proof of business premises",
        ],
        "key_provisions": ["Registration mandatory within 30 days"],
    },
    "Nagaland": {
        "act_name": "Nagaland Shops and Establishments Act",
        "authority": "Labour Department, Nagaland",
        "portal": "https://nagaland.gov.in",
        "fee_range": "Rs 100 - Rs 500",
        "validity": "3 years (renewable)",
        "timeline": "15-30 working days",
        "documents_required": [
            "PAN Card of proprietor",
            "Aadhaar Card of proprietor",
            "Proof of business premises",
        ],
        "key_provisions": ["Registration mandatory within 30 days"],
    },
    "Sikkim": {
        "act_name": "Sikkim Shops and Commercial Establishments Act",
        "authority": "Labour Department, Sikkim",
        "portal": "https://sikkim.gov.in",
        "fee_range": "Rs 100 - Rs 500",
        "validity": "3 years (renewable)",
        "timeline": "15-30 working days",
        "documents_required": [
            "PAN Card of proprietor",
            "Aadhaar Card of proprietor",
            "Proof of business premises",
        ],
        "key_provisions": ["Registration mandatory within 30 days"],
    },
    "Tripura": {
        "act_name": "Tripura Shops and Establishments Act, 1975",
        "authority": "Labour Department, Tripura",
        "portal": "https://tripura.gov.in",
        "fee_range": "Rs 100 - Rs 500",
        "validity": "3 years (renewable)",
        "timeline": "15-30 working days",
        "documents_required": [
            "PAN Card of proprietor",
            "Aadhaar Card of proprietor",
            "Proof of business premises",
        ],
        "key_provisions": ["Registration mandatory within 30 days"],
    },
    "Chandigarh": {
        "act_name": "Punjab Shops and Commercial Establishments Act, 1958 (as applicable to Chandigarh)",
        "authority": "Labour Department, Chandigarh",
        "portal": "https://chandigarh.gov.in",
        "fee_range": "Rs 100 - Rs 500",
        "validity": "3 years (renewable)",
        "timeline": "7-14 working days",
        "documents_required": [
            "PAN Card of proprietor",
            "Aadhaar Card of proprietor",
            "Proof of business premises",
        ],
        "key_provisions": ["Registration mandatory within 30 days"],
    },
    "Puducherry": {
        "act_name": "Puducherry Shops and Establishments Act",
        "authority": "Labour Department, Puducherry",
        "portal": "https://labour.py.gov.in",
        "fee_range": "Rs 100 - Rs 500",
        "validity": "3 years (renewable)",
        "timeline": "7-15 working days",
        "documents_required": [
            "PAN Card of proprietor",
            "Aadhaar Card of proprietor",
            "Proof of business premises",
        ],
        "key_provisions": ["Registration mandatory within 30 days"],
    },
    "Jammu and Kashmir": {
        "act_name": "Jammu & Kashmir Shops and Establishments Act",
        "authority": "Labour Department, J&K",
        "portal": "https://jk.gov.in",
        "fee_range": "Rs 100 - Rs 500",
        "validity": "3 years (renewable)",
        "timeline": "15-30 working days",
        "documents_required": [
            "PAN Card of proprietor",
            "Aadhaar Card of proprietor",
            "Proof of business premises",
        ],
        "key_provisions": ["Registration mandatory within 30 days"],
    },
    "Ladakh": {
        "act_name": "Ladakh Shops and Establishments Act",
        "authority": "Labour Department, Ladakh",
        "portal": "https://ladakh.gov.in",
        "fee_range": "Rs 100 - Rs 500",
        "validity": "3 years (renewable)",
        "timeline": "15-30 working days",
        "documents_required": [
            "PAN Card of proprietor",
            "Aadhaar Card of proprietor",
            "Proof of business premises",
        ],
        "key_provisions": ["Registration mandatory within 30 days"],
    },
}


class SolePropService:
    """Sole Proprietorship registration and guidance service."""

    # ------------------------------------------------------------------
    # GST Registration (REG-01)
    # ------------------------------------------------------------------

    def generate_gst_registration_data(
        self, owner_details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate GST REG-01 form data for a sole proprietor.

        GST registration is the primary formal registration for sole proprietors.
        """
        state = owner_details.get("state", "")

        # State code for GSTIN
        gst_state_codes: Dict[str, str] = {
            "Jammu and Kashmir": "01", "Himachal Pradesh": "02", "Punjab": "03",
            "Chandigarh": "04", "Uttarakhand": "05", "Haryana": "06",
            "Delhi": "07", "Rajasthan": "08", "Uttar Pradesh": "09",
            "Bihar": "10", "Sikkim": "11", "Arunachal Pradesh": "12",
            "Nagaland": "13", "Manipur": "14", "Mizoram": "15",
            "Tripura": "16", "Meghalaya": "17", "Assam": "18",
            "West Bengal": "19", "Jharkhand": "20", "Odisha": "21",
            "Chhattisgarh": "22", "Madhya Pradesh": "23", "Gujarat": "24",
            "Maharashtra": "27", "Andhra Pradesh": "37",
            "Karnataka": "29", "Goa": "30", "Kerala": "32",
            "Tamil Nadu": "33", "Puducherry": "34", "Telangana": "36",
            "Ladakh": "38",
        }

        state_code = gst_state_codes.get(state, "XX")

        return {
            "form_name": "GST REG-01",
            "form_version": "V1",
            "title": "Application for GST Registration - Sole Proprietor",
            "part_a": {
                "state": state,
                "state_code": state_code,
                "pan": owner_details.get("pan_number", ""),
                "email": owner_details.get("email", ""),
                "phone": owner_details.get("phone", ""),
            },
            "part_b": {
                "legal_name": owner_details.get("full_name", ""),
                "trade_name": owner_details.get("business_name", ""),
                "constitution_of_business": "Proprietorship",
                "date_of_commencement": owner_details.get("commencement_date", date.today().isoformat()),
                "pan": owner_details.get("pan_number", ""),
                "aadhaar": owner_details.get("aadhaar_number", ""),
                "principal_place_of_business": {
                    "address": owner_details.get("business_address", ""),
                    "state": state,
                    "pincode": owner_details.get("pincode", ""),
                    "nature_of_possession": owner_details.get("premises_type", "Rented"),
                },
                "bank_details": {
                    "account_number": owner_details.get("bank_account", ""),
                    "ifsc_code": owner_details.get("ifsc_code", ""),
                    "bank_name": owner_details.get("bank_name", ""),
                },
                "goods_and_services": {
                    "hsn_codes": owner_details.get("hsn_codes", []),
                    "sac_codes": owner_details.get("sac_codes", []),
                    "description": owner_details.get("business_description", ""),
                },
            },
            "documents_required": [
                "PAN Card of proprietor",
                "Aadhaar Card of proprietor",
                "Photograph of proprietor",
                "Proof of business premises (rent agreement / electricity bill)",
                "Bank statement / cancelled cheque",
                "NOC from landlord (if rented premises)",
            ],
            "metadata": {
                "generated_date": date.today().isoformat(),
                "portal": "https://reg.gst.gov.in",
                "filing_fee": 0,  # GST registration is free
                "processing_time": "3-7 working days",
                "note": (
                    "GST registration is mandatory if annual turnover exceeds Rs 40 lakh "
                    "(Rs 20 lakh for service providers in most states). Registration can be "
                    "obtained voluntarily even below the threshold."
                ),
            },
        }

    # ------------------------------------------------------------------
    # MSME / Udyam Registration
    # ------------------------------------------------------------------

    def generate_udyam_registration(
        self, owner_details: Dict[str, Any], business_details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate Udyam (MSME) Registration data for a sole proprietor.

        Udyam Registration is free, online, and based on self-declaration.
        """
        investment = business_details.get("investment", 0)
        turnover = business_details.get("turnover", 0)

        # Classify enterprise
        if investment <= 10000000 and turnover <= 50000000:  # 1Cr / 5Cr
            classification = "Micro Enterprise"
        elif investment <= 100000000 and turnover <= 500000000:  # 10Cr / 50Cr
            classification = "Small Enterprise"
        elif investment <= 500000000 and turnover <= 2500000000:  # 50Cr / 250Cr
            classification = "Medium Enterprise"
        else:
            classification = "Not eligible for MSME classification"

        return {
            "form_name": "Udyam Registration",
            "title": "MSME / Udyam Registration - Sole Proprietor",
            "portal": "https://udyamregistration.gov.in",
            "fields": {
                "aadhaar_number": owner_details.get("aadhaar_number", ""),
                "name_as_per_aadhaar": owner_details.get("full_name", ""),
                "pan": owner_details.get("pan_number", ""),
                "enterprise_name": business_details.get("business_name", ""),
                "type_of_organisation": "Proprietorship",
                "date_of_commencement": business_details.get(
                    "commencement_date", date.today().isoformat()
                ),
                "enterprise_type": business_details.get("type", "Service"),
                "major_activity": business_details.get("activity", ""),
                "nic_code": business_details.get("nic_code", ""),
                "investment_in_plant_and_machinery": investment,
                "annual_turnover": turnover,
                "classification": classification,
                "address": {
                    "business_address": business_details.get("address", ""),
                    "state": owner_details.get("state", ""),
                    "district": business_details.get("district", ""),
                    "pincode": business_details.get("pincode", ""),
                },
                "bank_details": {
                    "ifsc_code": business_details.get("ifsc_code", ""),
                    "account_number": business_details.get("bank_account", ""),
                },
            },
            "classification_criteria": {
                "micro": "Investment <= Rs 1 Cr AND Turnover <= Rs 5 Cr",
                "small": "Investment <= Rs 10 Cr AND Turnover <= Rs 50 Cr",
                "medium": "Investment <= Rs 50 Cr AND Turnover <= Rs 250 Cr",
            },
            "benefits": [
                "Priority sector lending from banks",
                "Collateral-free loans up to Rs 1 Cr under CGTMSE",
                "Lower interest rates on loans",
                "Protection against delayed payments (MSMED Act)",
                "Subsidy on patent and trademark registration",
                "Exemption from direct tax laws in initial years",
                "Government tender preference (up to 25% reservation)",
                "Access to technology upgradation schemes (CLCS-TUS)",
            ],
            "metadata": {
                "generated_date": date.today().isoformat(),
                "filing_fee": 0,  # Udyam registration is free
                "processing_time": "Instant (online, Aadhaar-based)",
                "validity": "Permanent (no renewal required)",
                "note": (
                    "Udyam Registration is based on self-declaration. No documents "
                    "or proof needs to be uploaded. The registration is linked to the "
                    "proprietor's Aadhaar number."
                ),
            },
        }

    # ------------------------------------------------------------------
    # Shop & Establishment Act Guidance
    # ------------------------------------------------------------------

    def get_shop_act_guidance(self, state: str) -> Dict[str, Any]:
        """
        Return state-specific Shop & Establishment Act guidance.

        Covers all 31 states and union territories.
        """
        guidance = SHOP_ACT_GUIDANCE.get(state)

        if guidance:
            return {
                "success": True,
                "state": state,
                "guidance": guidance,
                "general_note": (
                    "Shop & Establishment registration is mandatory for all commercial "
                    "establishments within 30 days of commencement of business. "
                    "This is a state-level registration and requirements may vary."
                ),
            }

        # Fallback for states not specifically covered
        return {
            "success": True,
            "state": state,
            "guidance": {
                "act_name": f"{state} Shops and Establishments Act",
                "authority": f"Labour Department, {state}",
                "portal": "Contact the local Labour Department",
                "fee_range": "Rs 100 - Rs 1,000 (approximate)",
                "validity": "3-5 years (renewable)",
                "timeline": "10-30 working days",
                "documents_required": [
                    "PAN Card of proprietor",
                    "Aadhaar Card of proprietor",
                    "Proof of business premises",
                    "Passport-size photograph",
                ],
                "key_provisions": [
                    "Registration mandatory within 30 days of commencement",
                    "Working hours and weekly holidays as per state rules",
                ],
            },
            "general_note": (
                f"Specific details for {state} may vary. Please contact the local "
                f"Labour Department for the most current requirements and fees."
            ),
        }


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------
sole_prop_service = SolePropService()
