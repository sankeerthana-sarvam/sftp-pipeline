import paramiko
import logging
from typing import Optional
from dotenv import load_dotenv
import os 

load_dotenv()

class AzureStorageSFTP:
    def __init__(self, 
                 hostname: str = os.getenv('SFTP_SERVER'),
                 username: str = os.getenv('SFTP_USERNAME'),
                 password: str = os.getenv('SFTP_PASSWORD'),
                 port: int = int(os.getenv('SFTP_PORT', 22))):
        self.hostname = hostname
        self.username = username
        self.password = password
        self.port = port
        self.sftp = None
        self.transport = None
                
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def connect(self) -> bool:
        try:
            self.transport = paramiko.Transport((self.hostname, self.port))
            
            self.transport.connect(username=self.username, password=self.password)
            
            self.sftp = paramiko.SFTPClient.from_transport(self.transport)
            
            self.logger.info(f"Successfully connected to {self.hostname}")
            return True
            
        except paramiko.AuthenticationException:
            self.logger.error("Authentication failed. Please check credentials.")
            return False
        except paramiko.SSHException as ssh_exception:
            self.logger.error(f"SSH exception occurred: {str(ssh_exception)}")
            return False
        except Exception as e:
            self.logger.error(f"Connection failed: {str(e)}")
            return False

    def list_directory(self, path='/') -> Optional[list]:
        try:
            if self.sftp:
                return self.sftp.listdir(path)
            else:
                self.logger.error("No active SFTP connection")
                return None
        except Exception as e:
            self.logger.error(f"Error listing directory: {str(e)}")
            return None

    def upload_file(self, local_path: str, remote_path: str) -> bool:
        try:
            if self.sftp:
                self.sftp.put(local_path, remote_path)
                self.logger.info(f"Successfully uploaded {local_path} to {remote_path}")
                return True
            else:
                self.logger.error("No active SFTP connection")
                return False
        except Exception as e:
            self.logger.error(f"Error uploading file: {str(e)}")
            return False

    def download_file(self, remote_path: str, local_path: str) -> bool:
        try:
            if self.sftp:
                self.sftp.get(remote_path, local_path)
                self.logger.info(f"Successfully downloaded {remote_path} to {local_path}")
                return True
            else:
                self.logger.error("No active SFTP connection")
                return False
        except Exception as e:
            self.logger.error(f"Error downloading file: {str(e)}")
            return False
        
    def delete_file(self, remote_path):
        try:
            if self.sftp:
                self.sftp.remove(remote_path)
                self.logger.info(f"Successfully deleted {remote_path}")
                return True 
            else:
                self.logger.erro("No active SFTP connection")
                return False 
        
        except Exception as e:
            self.logger.error((f"Error deleting file: {str(e)}"))
            return False 

    def close(self):
        if self.sftp:
            self.sftp.close()
        if self.transport:
            self.transport.close()
        self.logger.info("Connection closed")


if __name__ == "__main__":
        
    azure_sftp = AzureStorageSFTP()

    if azure_sftp.connect():
        files = azure_sftp.list_directory()
        print(files)
        if files:
            print("Files in directory:", files)
        
        # azure_sftp.upload_file('Worksheet.xlsx', 'remote_file.xlsx')
        
        # azure_sftp.download_file('remote_file.xlsx', 'downloaded_file.xlsx')

        # azure_sftp.delete_file('remote_file.xlsx')
        
        azure_sftp.close()


    
    
