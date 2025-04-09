import logging
import tempfile
import os
import json
import csv
import pandas as pd
import asyncio
from sftp_client import AzureStorageSFTP
import end_to_end_scheduling

logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def download_and_process_sftp_file():
    try:
        # Get temp directory path for file operations
        temp_dir = tempfile.gettempdir()
        logger.info(f"Using temp directory: {temp_dir}")
        
        # Create full paths for files using temp directory
        csv_file_path = os.path.join(temp_dir, "downloaded_test.csv")
        json_file_path = os.path.join(temp_dir, "user_records.json")
        
        azure_sftp = AzureStorageSFTP()
        
        if azure_sftp.connect():
            files = azure_sftp.list_directory()
            azure_sftp.download_file('test.csv', csv_file_path)
            azure_sftp.close()
            logger.info(f"Successfully downloaded file to {csv_file_path}")
        else:
            logger.error("Failed to connect to SFTP server")
            return
            
        # logging.info("Processing downloaded CSV file")
        
        # data = []
        
        # with open(csv_file_path, encoding="utf-16") as f:
        #     data = list(csv.DictReader(f, delimiter="\t"))
        
        # user_records_list = [end_to_end_scheduling.create_user_records(dp) for dp in data]
        # user_records_json = {"user_records": user_records_list}
        
        # with open(json_file_path, "w") as json_file:
        #     json.dump(user_records_json, json_file)
        #     logging.info(f"Successfully wrote JSON to {json_file_path}")
        
        # # csv_output_path = os.path.join(temp_dir, "user_records.csv")
        # # df = pd.json_normalize(user_records_json['user_records'], sep='_')
        # # df.to_csv(csv_output_path, index=False)
        
        # logging.info("Starting call scheduling process")
      
        # access_token = asyncio.run(end_to_end_scheduling.get_access_token())
        # if not access_token:
        #     logging.error("Failed to get access token")
        #     return
            
        # cohort_id = asyncio.run(end_to_end_scheduling.create_cohort_request(json_file_path, access_token))
        # if not cohort_id:
        #     logging.error("Failed to create cohort")
        #     return
            
        # campaign_result = asyncio.run(end_to_end_scheduling.create_campaign_request(cohort_id, access_token))
        # if campaign_result is False:
        #     logging.error("Failed to create campaign") 
        # else:
        #     logging.info("Successfully completed end-to-end scheduling")
            
    except Exception as e:
        logger.error(f'Error executing application code: {str(e)}')
        logger.exception("Detailed error information:")

    logger.info('Function executed successfully.')

# This allows the script to be run directly
if __name__ == "__main__":
    download_and_process_sftp_file()

