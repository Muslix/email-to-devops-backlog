import requests
import base64
from log_config import setup_logging
logger = setup_logging()

def upload_attachment_to_devops(organization, project, bug_id, filename, content, personal_access_token):
    url = f"https://dev.azure.com/{organization}/{project}/_apis/wit/attachments?fileName={filename}&api-version=6.0"
    headers = {
        "Authorization": f"Basic {base64.b64encode(f':{personal_access_token}'.encode()).decode()}",
        "Content-Type": "application/octet-stream"
    }
    response = requests.post(url, headers=headers, data=content)
    if response.status_code == 201:
        attachment_url = response.json()['url']
        add_attachment_to_bug(organization, project, bug_id, filename, attachment_url, personal_access_token)
    else:
        logger.error(f"Failed to upload attachment: {response.status_code} - {response.text}")


def add_attachment_to_bug(organization, project, bug_id, filename, attachment_url, personal_access_token):
    url = f"https://dev.azure.com/{organization}/{project}/_apis/wit/workitems/{bug_id}?api-version=6.0"
    headers = {
        "Authorization": f"Basic {base64.b64encode(f':{personal_access_token}'.encode()).decode()}",
        "Content-Type": "application/json-patch+json"
    }
    payload = [
        {
            "op": "add",
            "path": "/relations/-",
            "value": {
                "rel": "AttachedFile",
                "url": attachment_url,
                "attributes": {
                    "name": filename
                }
            }
        }
    ]
    response = requests.patch(url, headers=headers, json=payload)
    if response.status_code != 200:
        logger.error(f"Failed to add attachment to bug: {response.status_code} - {response.text}")

def create_devops_issue(title, description, personal_access_token, organization, project):
    url = f"https://dev.azure.com/{organization}/{project}/_apis/wit/workitems/$Bugs?api-version=6.0"
    b64_pat = base64.b64encode(f":{personal_access_token}".encode()).decode()
    headers = {
        "Authorization": f"Basic {b64_pat}",
        "Content-Type": "application/json-patch+json"
    }
    payload = [
        {
            "op": "add",
            "path": "/fields/System.Title",
            "value": title,
        },
        {
            "op": "add",
            "path": "/fields/System.Description",
            "value": description,
        },
        {
            "op": "add",
            "path": "/fields/Microsoft.VSTS.Common.Severity",
            "value": "3 - Medium"
        },
        {
            "op": "add",
            "path": "/fields/Microsoft.VSTS.Common.Priority",
            "value": "2"
        }
    ]
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        logger.info("Azure DevOps Bug successfully created.")
        return response.json()['id']
    else:
        logger.error(f"Error creating Azure DevOps Bug: {response.status_code} - {response.text}")
        return None

