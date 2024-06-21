import requests
import json

# Set your endpoint URL and access token
def get_access_token():
    auth_url = 'https://auth.app.wiz.io/oauth/token'
    auth_payload = {
        'grant_type': 'client_credentials',
        'client_id': '4l3g2yogdfdlle22wvxsjk4tlro4ijspksifcamug225j5qajymhg',
        'client_secret': 'ZHlDZdrfdLRNPtoYWXc99MqtqBQebn417A9pMas8D4TtdWxww1ubvVNDmUwj7ugO',
        'audience': 'wiz-api'
    }
    auth_headers = {
        'content-type': 'application/x-www-form-urlencoded'
    }

    auth_response = requests.post(auth_url, data=auth_payload, headers=auth_headers)
    auth_response.raise_for_status()
    token = auth_response.json().get('access_token')
    return token
token = get_access_token()
ENDPOINT_URL = "https://api.us57.app.wiz.io/graphql"

# Output file name
OUTPUT_FILE = "corporate_wiz_accounts.json"

# GraphQL query and variables
QUERY = '''
query CloudAccountsPage($filterBy: CloudAccountFilters, $first: Int, $after: String) {
  cloudAccounts(filterBy: $filterBy, first: $first, after: $after) {
    nodes {
      id
      externalId
      linkedProjects {
        id
        name
      }
    }
    pageInfo {
      hasNextPage
      endCursor
    }
  }
}
'''
VARIABLES = {"first": 500}

# Function to make GraphQL requests
def graphql_query(query, variables):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    data = {"query": query, "variables": variables}
    response = requests.post(ENDPOINT_URL, headers=headers, json=data)
    response.raise_for_status()
    return response.json()

# Function to extract desired fields from response
# Function to extract desired fields from response
def extract_fields(response):
    nodes = response["data"]["cloudAccounts"]["nodes"]
    extracted_data = []
    
    for node in nodes:
        if node["linkedProjects"] is not None:
            linked_projects = [{"id": project["id"], "name": project["name"]} for project in node["linkedProjects"]]
        else:
            linked_projects = []
        
        extracted_node = {
            "id": node["id"],
            "externalId": node["externalId"],
            "linkedProjects": linked_projects
        }
        
        extracted_data.append(extracted_node)
    
    return extracted_data


# Array to accumulate results
results = []

# Initial request
response = graphql_query(QUERY, VARIABLES)
results.extend(extract_fields(response))

# Pagination loop
has_next_page = response["data"]["cloudAccounts"]["pageInfo"]["hasNextPage"]
end_cursor = response["data"]["cloudAccounts"]["pageInfo"]["endCursor"]

while has_next_page:
    variables = {"first": 500, "after": end_cursor}
    response = graphql_query(QUERY, variables)
    results.extend(extract_fields(response))
    has_next_page = response["data"]["cloudAccounts"]["pageInfo"]["hasNextPage"]
    end_cursor = response["data"]["cloudAccounts"]["pageInfo"]["endCursor"]

# Write results to JSON file
with open(OUTPUT_FILE, "w") as f:
    json.dump({"cloudAccounts": results}, f, indent=2)

print(f"Output written to {OUTPUT_FILE}")