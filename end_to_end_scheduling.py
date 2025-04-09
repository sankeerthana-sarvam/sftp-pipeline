import pandas as pd
import asyncio
from datetime import datetime, timezone, timedelta
import httpx
import logging
import json
import csv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

base_url = "https://apps.sarvam.ai"
org_id = "tatacapital.com"  
workspace_id = "tatacapital-com-de-aba4a4"       
app_id = "tata-test-c3e02d6d-38c7"    

def create_user_records(dp):

    hdfc_premium = dp.get('HDFCLifeInusrancePremiumTPP', '0')
    tata_premium = dp.get('TATAAIGGeneralInsuranceTPP', '0')
    
    hdfc_premium = '0' if pd.isna(hdfc_premium) else str(hdfc_premium).replace(',', '')
    tata_premium = '0' if pd.isna(tata_premium) else str(tata_premium).replace(',', '')
    
    hdfc_premium = '0' if hdfc_premium == "" else hdfc_premium
    tata_premium = '0' if tata_premium == "" else tata_premium

    insurance_premium = float(hdfc_premium) + float(tata_premium)
    
    return {                    
        "phone_number": dp['PrimaryMobileNumber'],  
        "agent_variables": {    
            "interest_rate": f"{dp['InterestRate']}%",
            "loan_account_number": dp["LoanID"][-4:],
            "disbursed_amount": f"{dp['DisbursedLoanAmount']} rupees",
            "loan_type": "Personal Loan" if dp["ProductCode"] == "PL" else "Two Wheeler Loan",     
            "emi_start_date": dp["FirstEMIDate_N"].replace("-","/").lstrip("0").replace("/0", "/"), 
            "emi_end_date": dp["LastEMIDate_N"].replace("-","/").lstrip("0").replace("/0", "/"),
            "emi_cycle": "monthly",  
            "insurance_type": "general",    
            "insurance_company": "Tata AIG",   
            "alternate_number": "",
            "get_information_on_whatsapp": "false",
            "customer_name": next((word.title() for word in dp["CustomerName"].lower().split() if len(word) > 2 and word.lower() not in ['mrs', 'mr', 'miss', 'ms']), dp["CustomerName"].lower().title()),
            "loan_duration": f"{dp['Tenure']} months",
            "disposition": "didn't reach verification",     # change this maybe
            "verbal_commit": "",    
            "alternate_date": "",   
            "alternate_time": "",
            "overall_feedback": "",
            "is_insured": "true" if insurance_premium > 0 else "false",     
            "correct_address": "",
            "user_address": ", ".join([
                addr.lower().title().replace(" Nr ", " Near ")
                for addr in [dp["AddressLine1"], dp["AddressLine2"]]
            ]),
            "insurance_premium": f"{insurance_premium} rupees",
            "request_call_back" : "false",
            "call_success": "false",      ##
            "user_identity": "",   
            "received_on_phone": "true",
            "received_on_email": "true",
            "num_valid_details": "0",
            "alternate_number_case_id": "",
            "whatsapp_opt_in_case_id": "",
            "customer_feedback_case_id": "",
            "address_verification_case_id": "",
            "call_disposition_case_id": "",
            "disbursal_date" : dp["DisbursalDate_N"].replace("-","/").lstrip("0").replace("/0", "/"),
            "num_consecutive_failures": "0",
            "dob": "",
            "sanction_amount": "",
            "emi_amount": "",
            "dispute": "false",
            "bank_name": dp.get("BankName", "").lower().title(),
        },
        
        "internal_variables": {
            "contract_id": dp["LoanID"],      
            "bot_phone_number": "919240247000",
            "channel_type": "tata_tele",
            # "dob": tuple(dp["DateOfBirth"].split("/")) if '/' in dp["DateOfBirth"] else tuple(dp["DateOfBirth"].split("-")) ,
            "dob": dp["DateOfBirth"].replace("-","/"),         #can be both / and - 
            "sanction_amount": str(dp["SanctionedLoanAmount"]).replace(",", "").replace("-", "").replace(" ", ""),   
            "emi_amount": str(dp["OriginalEMIAmount"]).replace(",", "").replace("-", "").replace(" ", ""),
        },
        
        "app_overrides": {},
        
        "user_channel_metadata": {"tata_tele": {}}
    }

async def get_access_token():
   
    try:
        async with httpx.AsyncClient() as client:
            login_response = await client.post(
                f"{base_url}/api/auth/login",
                json={
                    "org_id": org_id,
                    "user_id": "sarvam-admin@tatacapital.com",
                    "password": "g$2!@%hal*9l",
                },
                timeout=60, 
            )
            login_response.raise_for_status()
            access_token = login_response.json().get("access_token")
            logger.info("Access token obtained successfully.")
            return access_token
    except Exception as e:
        logger.error(f"Error logging in: {e}")
        raise

async def create_cohort_request(json_file_path, access_token):
    cohort_url = f"{base_url}/api/scheduling/orgs/{org_id}/workspaces/{workspace_id}/cohorts"
    headers = {
        "Authorization": f"Bearer {access_token}",  
    }
    data = {
        "name": "test-cohort",  
    }
    with open(json_file_path, "rb") as json_file:
        files = {
            "file": ("user_records.json", json_file, "application/json")
        }

        async with httpx.AsyncClient() as client:   
            try:
                response = await client.post(cohort_url, headers=headers, data=data, files=files)
                response_data = response.json()
                logger.info(f"Cohort creation response: {response_data}")
                response.raise_for_status()
                return response_data.get("cohort_id")
            except Exception as e:
                logger.error(f"Error creating cohort: {e}")
                raise
            
async def create_campaign_request(cohort_id, access_token):
    campaign_url = f"{base_url}/api/scheduling/orgs/{org_id}/workspaces/{workspace_id}/campaigns"
    
    payload = {
        "name": "test-campaign",
        "description": "This is a live campaign",
        "app_id": app_id,
        "cohort_id": cohort_id,
        "start_timestamp": (datetime.now(timezone.utc) + timedelta(minutes=10)).isoformat(),
        "end_timestamp": (datetime.now(timezone.utc) + timedelta(days=12)).isoformat(),
        "allowed_schedule": {
            "allowed_start_time": "10:00",
            "allowed_end_time": "18:59",  
            "allowed_days": [
                "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"
            ]
        },
    }

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                campaign_url,
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            logger.info(f"Campaign creation response: {response.json()}")
            return True
        except httpx.HTTPStatusError as exc:
            logger.error(f"HTTP Error occurred: {exc.response.status_code} - {exc.response.text}")
            return False
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            return False


if __name__ == "__main__":

    access_token = asyncio.run(get_access_token())
    cohort_id = asyncio.run(create_cohort_request())
    asyncio.run(create_campaign_request(cohort_id))

