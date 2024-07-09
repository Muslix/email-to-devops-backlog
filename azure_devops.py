import requests
import base64
from fuzzywuzzy import fuzz
import spacy
from log_config import setup_logging

logger = setup_logging()
nlp = spacy.load('en_core_web_md')

def is_spam(content):
    doc = nlp(content.lower())
    spam_indicators = ["free", "click here", "subscribe", "credit", "offer", "winner", "prize", "buy", "discount"]
    if any(token.text in spam_indicators for token in doc):
        return True
    return False

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

def search_existing_bugs(title, personal_access_token, organization, project):
    url = f"https://dev.azure.com/{organization}/{project}/_apis/wit/wiql?api-version=6.0"
    query = {
        "query": "SELECT [System.Id], [System.Title], [System.Description] FROM WorkItems WHERE [System.WorkItemType] = 'Bug'"
    }
    b64_pat = base64.b64encode(f":{personal_access_token}".encode()).decode()
    headers = {
        "Authorization": f"Basic {b64_pat}",
        "Content-Type": "application/json"
    }
    response = requests.post(url, headers=headers, json=query)
    if response.status_code == 200:
        return response.json()["workItems"]
    else:
        logger.error(f"Error searching Azure DevOps Bugs: {response.status_code} - {response.text}")
        return []

def get_bug_details(bug_id, personal_access_token, organization, project):
    url = f"https://dev.azure.com/{organization}/{project}/_apis/wit/workitems/{bug_id}?api-version=6.0"
    b64_pat = base64.b64encode(f":{personal_access_token}".encode()).decode()
    headers = {
        "Authorization": f"Basic {b64_pat}",
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        logger.error(f"Error retrieving Azure DevOps Bug details: {response.status_code} - {response.text}")
        return None

def similar_description(desc1, desc2):
    # Use fuzzy matching for simple similarity check
    fuzz_ratio = fuzz.ratio(desc1, desc2)

    # Use SpaCy for advanced similarity check
    doc1 = nlp(desc1)
    doc2 = nlp(desc2)
    spacy_similarity = doc1.similarity(doc2)

    # Combine both scores for a final decision
    combined_score = (fuzz_ratio + spacy_similarity * 100) / 2

    logger.info(f"Fuzz ratio: {fuzz_ratio}, SpaCy similarity: {spacy_similarity}, Combined score: {combined_score}")

    return combined_score > 70  # Threshold for determining similarity

def bug_already_exists(title, description, personal_access_token, organization, project):
    existing_bugs = search_existing_bugs(title, personal_access_token, organization, project)
    for bug in existing_bugs:
        bug_id = bug["id"]
        bug_details = get_bug_details(bug_id, personal_access_token, organization, project)
        if bug_details and similar_description(description, bug_details["fields"]["System.Description"]):
            return bug_id  # Return bug ID if similar bug exists
    return None


def create_devops_issue(title, description, email_sender, personal_access_token, organization, project):
    existing_bug_id = bug_already_exists(title, description, personal_access_token, organization, project)
    if existing_bug_id:
        logger.info(f"A similar bug already exists with ID {existing_bug_id}. Updating the existing bug.")
        update_bug(existing_bug_id, email_sender, personal_access_token, organization, project)
        return existing_bug_id

    url = f"https://dev.azure.com/{organization}/{project}/_apis/wit/workitems/$Bug?api-version=6.0"
    b64_pat = base64.b64encode(f":{personal_access_token}".encode()).decode()
    headers = {
        "Authorization": f"Basic {b64_pat}",
        "Content-Type": "application/json-patch+json"
    }

    formatted_description = description.replace("\n", "<br>")

    payload = [
        {
            "op": "add",
            "path": "/fields/System.Title",
            "value": title,
        },
        {
            "op": "add",
            "path": "/fields/System.Description",
            "value": formatted_description,
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
        },
        {
            "op": "add",
            "path": "/fields/ReportedCount",
            "value": 1
        }
    ]
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        logger.info("Azure DevOps Bug successfully created.")
        return response.json()['id']
    else:
        logger.error(f"Error creating Azure DevOps Bug: {response.status_code} - {response.text}")
        return None

def update_bug(bug_id, email_sender, personal_access_token, organization, project):
    current_details = get_bug_details(bug_id, personal_access_token, organization, project)
    if not current_details:
        logger.error(f"Failed to retrieve the bug details for bug ID: {bug_id}")
        return

    current_reported_count = current_details.get('fields', {}).get('Custom.ReportedCount', 0)
    new_reported_count = current_reported_count + 1

    url = f"https://dev.azure.com/{organization}/{project}/_apis/wit/workitems/{bug_id}?api-version=6.0"
    headers = {
        "Authorization": f"Basic {base64.b64encode(f':{personal_access_token}'.encode()).decode()}",
        "Content-Type": "application/json-patch+json"
    }

    payload = [
        {"op": "add", "path": "/fields/System.History", "value": f"Bug occurrence reported by {email_sender}."},
        {"op": "replace", "path": "/fields/ReportedCount", "value": new_reported_count}
    ]

    response = requests.patch(url, headers=headers, json=payload)
    if response.status_code != 200:
        logger.error(f"Failed to update the bug: {response.status_code} - {response.text}")
    else:
        logger.info(f"Bug {bug_id} updated successfully with new ReportedCount {new_reported_count}")
