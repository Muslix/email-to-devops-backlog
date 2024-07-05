import requests
import base64
from log_config import setup_logging
logger = setup_logging()

def create_devops_issue(title, description, personal_access_token, organization, project):
    url = f"https://dev.azure.com/{organization}/{project}/_apis/wit/workitems/$Issue?api-version=6.0"
    b64_pat = base64.b64encode(bytes(f":{personal_access_token}", 'utf-8')).decode('ascii')
    headers = {
        "Authorization": f"Basic {b64_pat}",
        "Content-Type": "application/json-patch+json"
    }
    payload = [
        {"op": "add", "path": "/fields/System.Title", "value": title},
        {"op": "add", "path": "/fields/System.Description", "value": description}
    ]
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        logger.info("Azure DevOps issue successfully created.")
    else:
        logger.error("Error creating Azure DevOps issue:")
        logger.error("Body: %s", description)
        logger.error("Title: %s", title)
        logger.error("Response: %s", response)
