## Webapp using FASTAPI#
import subprocess
import os


from fastapi import FastAPI
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware

import google
import json

from google.auth import default
from google.cloud import storage


import logging

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def set_gcp_project(project_id):
    """Sets the current GCP project ID."""
    os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
    print(f"GCP project set to: {project_id}")



# Get credentials automatically
credentials, project_id = default()
print ("project_id: ", project_id)


def gcloud_login():
    """Calls 'gcloud auth login' and handles potential errors."""
    try:
        result = subprocess.run(
            ["gcloud", "auth", "login"], 
            check=True, 
            capture_output=True, 
            text=True, 
        )
        print("Authentication successful!")
        print(f"Credentials saved to: {os.path.expanduser('~/.config/gcloud/credentials.db')}") 
    except subprocess.CalledProcessError as e:
        print(f"Authentication failed with error: {e.stderr}")

def gcloud_logout():
    """Revokes current gcloud credentials, effectively logging out."""
    try:
        result = subprocess.run(
            ["gcloud", "auth", "revoke", "all"], 
            check=True,  
            capture_output=True, 
            text=True,
        )
        print("Logged out successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Logout failed with error: {e.stderr}")


def is_logged_in():
    """Checks if valid GCP credentials exist."""
    try:
        # Check for application default credentials
        credentials, p_id = google.auth.default()
        print ("Project: ID:: ", p_id)
        if not credentials.valid:  # Refresh if expired
            credentials.refresh(google.auth.transport.requests.Request())
        return credentials.valid
    except google.auth.exceptions.DefaultCredentialsError:
        return False


@app.get("/getFilesFromBucket/{bucket_name}")
def list_bucket_files_as_json(bucket_name):
    """Lists all file names in the specified GCP bucket and returns them as JSON."""
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blobs = bucket.list_blobs()  # Get all blobs (files and folders)
        file_names = [blob.name for blob in blobs if not blob.name.endswith("/")]  # Filter out folders
        res =  json.dumps(file_names, indent=2)  # Formatted JSON for readability
        print (res)
        return res

    
    except Exception as e:
        return json.dumps({"error": str(e)})  # Return error as JSON
    

@app.get("/getBuckets")
def list_buckets_as_json():
    """Lists all buckets in the specified GCP project and returns them as JSON."""
    try:
        storage_client = storage.Client()
        buckets = storage_client.list_buckets()
        bucket_names = [bucket.name for bucket in buckets]  # Filter out folders
        
        res =  json.dumps(bucket_names, indent=2)  # Formatted JSON for readability
        print (res)
        return res
    except Exception as e:
        return json.dumps({"error": str(e)})


@app.get("/")
async def main(request: Request):
    return JSONResponse(content={"Available APIs": ["/getBuckets", "/getFilesFromBucket/{bucket_name}"]}, status_code=200)




def init():
    if is_logged_in():
        print("GCP authentication is valid!")
    else:
        print("Not logged into GCP or credentials are invalid.")
        set_gcp_project('scratchzone')
        gcloud_login()
        


#list_bucket_files_as_json("pdfsfortesting0716")    
list_buckets_as_json()
list_bucket_files_as_json("pdfsfortesting0716")