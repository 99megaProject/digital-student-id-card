# utils.py
import dropbox
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_dropbox_client():
    """
    Initializes and returns a Dropbox client instance using
    the long-lived refresh token.
    """
    APP_KEY = os.getenv("DROPBOX_APP_KEY")
    APP_SECRET = os.getenv("DROPBOX_APP_SECRET")
    REFRESH_TOKEN = os.getenv("DROPBOX_REFRESH_TOKEN")

    if not all([APP_KEY, APP_SECRET, REFRESH_TOKEN]):
        print("ERROR: Missing one or more Dropbox environment variables.")
        print("Please check your .env file for:")
        print("  - DROPBOX_APP_KEY")
        print("  - DROPBOX_APP_SECRET")
        print("  - DROPBOX_REFRESH_TOKEN")
        return None

    try:
        # Create a Dropbox client instance
        # This instance will automatically use the refresh token
        # to get new short-lived access tokens as needed.
        dbx = dropbox.Dropbox(
            app_key=APP_KEY,
            app_secret=APP_SECRET,
            oauth2_refresh_token=REFRESH_TOKEN
        )
        
        # Check connection by getting user account info
        account = dbx.users_get_current_account()
        print(f"Successfully connected to Dropbox account: {account.name.display_name}")
        return dbx
        
    except dropbox.exceptions.AuthError as e:
        print(f"Error authenticating with Dropbox: {e}")
        print("This may be due to an invalid REFRESH_TOKEN or incorrect APP_KEY/APP_SECRET.")
        return None
    except Exception as e:
        print(f"Error during Dropbox initialization: {e}")
        return None

  
def upload_file(dbx, local_path, dropbox_path):
    """Uploads a file from a local path to a Dropbox path."""
    
    # Check if the local file exists
    if not os.path.exists(local_path):
        print(f"Error: Local file not found at '{local_path}'")
        return False

    try:
        with open(local_path, "rb") as f:
            # files_upload uploads the file and overwrites it if it exists
            dbx.files_upload(
                f.read(),
                dropbox_path,
                mode=dropbox.files.WriteMode('overwrite')
            )
        print(f"SUCCESSFULLY UPLOADED: '{local_path}' to Dropbox path '{dropbox_path}'")
        return True
        
    except dropbox.exceptions.ApiError as e:
        print(f"Error uploading file (API Error): {e}")
    except Exception as e:
        print(f"Error uploading file (General Error): {e}")
    return False
