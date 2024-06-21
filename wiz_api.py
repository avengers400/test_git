import requests
import json

# Set your token request details
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

# Get the access token
auth_response = requests.post(auth_url, data=auth_payload, headers=auth_headers)
token = auth_response.json().get('access_token')
print(f"Access Token: {token}")

# Set the GraphQL query and variables
query = """
query CloudConfigurationSettingsTable($first: Int, $after: String, $filterBy: CloudConfigurationRuleFilters, $orderBy: CloudConfigurationRuleOrder, $projectId: [String!]) { 
    cloudConfigurationRules(first: $first after: $after filterBy: $filterBy orderBy: $orderBy) { 
        analyticsUpdatedAt 
        nodes { 
            id 
            shortId 
            name 
            description 
            enabled 
            severity 
            serviceType 
            cloudProvider 
            subjectEntityType 
            functionAsControl 
            opaPolicy 
            builtin 
            targetNativeTypes 
            remediationInstructions 
            hasAutoRemediation 
            supportsNRT 
            createdAt 
            updatedAt 
            originalConfigurationRuleOverridden 
            control { 
                id 
            } 
            iacMatchers { 
                id 
                type 
                regoCode 
                parameters { 
                    ... on CloudConfigurationRuleAdmissionControllerMatcherParameters { 
                        operation 
                    } 
                } 
            } 
            matcherTypes 
            securitySubCategories { 
                id 
                title 
                description 
                category { 
                    id 
                    name 
                    description 
                    framework { 
                        id 
                        name 
                        enabled 
                    } 
                } 
            } 
            analytics(selection: {projectId: $projectId}) { 
                passCount 
                failCount 
            } 
            scopeAccounts { 
                id 
                name 
                cloudProvider 
            } 
            scopeProject { 
                id 
                name 
            } 
            tags { 
                key 
                value 
            } 
        } 
        pageInfo { 
            endCursor 
            hasNextPage 
        } 
        totalCount 
    } 
}
"""

variables = {
    "first": 500,
    "filterBy": {"frameworkCategory": []},
    "orderBy": {"field": "FAILED_CHECK_COUNT", "direction": "DESC"}
}

url = "https://api.us57.app.wiz.io/graphql"
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

all_responses = []
response = requests.post(url, json={"query": query, "variables": variables}, headers=headers)
response_data = response.json()

# Collect nodes from the first response
all_responses.extend(response_data['data']['cloudConfigurationRules']['nodes'])

# Pagination loop
while response_data['data']['cloudConfigurationRules']['pageInfo']['hasNextPage']:
    end_cursor = response_data['data']['cloudConfigurationRules']['pageInfo']['endCursor']
    variables['after'] = end_cursor
    response = requests.post(url, json={"query": query, "variables": variables}, headers=headers)
    response_data = response.json()
    
    # Collect nodes from subsequent responses
    all_responses.extend(response_data['data']['cloudConfigurationRules']['nodes'])
    



# Extract relevant data
final_res = [{'rule_name': node['name'], 'rule_id': node['id']} for node in all_responses]
print(len(final_res))

# Write the extracted data to a JSON file
print(all_responses)
with open('wiz_prod_rules.json', 'w') as json_file:
        json.dump(final_res, json_file, indent=4)

print("Data has been written to final_result.json")
