import json
import requests
import concurrent.futures
import pandas as pd
from datetime import datetime
import os
import warnings
import urllib3
import csv

# Suppress the InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Define the ratings
ratings = {
    "Device details": "LOW",
    "Device information": "LOW",
    "NTP Information": "MEDIUM",
    "SNMP Information": "MEDIUM",
    "Version info": "HIGH",
    "Global Settings": "MEDIUM",
    "Banner Settings": "LOW",
    "DNS Settings": "HIGH",
    "Disable Insecure Services": "HIGH",
    "Syslog Server Settings": "MEDIUM",
    "Forbid DHCP Server Service": "MEDIUM",
    "Password Policy Settings": "HIGH",
    "SSH Settings": "HIGH",
    "Restrict Login Attempts": "HIGH",
    "Enable IP to MAC address binding": "MEDIUM",
    "ICMP Message Verification": "MEDIUM",
    "Time out Settings": "MEDIUM"
}
devices = []


def fetch_devices(username_, password_):
    url = "https://fwaas.mhf.mhc/fa/server/connection/login"

    payload = json.dumps({
        "username": username_,
        "password": password_
    })
    headers = {
        'Content-Type': 'application/json'
    }

    try:
        response = requests.request("POST", url, headers=headers, data=payload, verify=False)
        res_login_status = response.json()['status']
        
        res_login = response.json()

        if res_login_status:
            print("Logged In Successfully")
            if 'SessionID' in res_login:
                res_login_sessionId = res_login['SessionID']
                headers = {
                    'Cookie': f'{res_login_sessionId}; PHPSESSID={res_login_sessionId}'
                }

                res_firewall_groups = requests.get("https://fwaas.mhf.mhc/afa/api/v1/device/FW", headers=headers, verify=False)
                report_name=res_firewall_groups.json()['lastReport']

                for group in res_firewall_groups.json()['deviceExtendedInfo']['firewallsInGroup']:
                    res_device_firewall_groups = requests.get(f'https://fwaas.mhf.mhc/afa/api/v1/device/{group}', headers=headers, verify=False)
                    
                    if res_device_firewall_groups.json()['type'] == "firewall":
                        devices.append(res_device_firewall_groups.json()['treeName'])
                    elif res_device_firewall_groups.json()['type'] == "group":
                        for device_group_1 in res_device_firewall_groups.json()['deviceExtendedInfo']['firewallsInGroup']:
                            res_groups_data_1 = requests.get(f"https://fwaas.mhf.mhc/afa/api/v1/device/{device_group_1}", headers=headers, verify=False)
                            
                            if res_groups_data_1.json()['type'] == "firewall":
                                devices.append(res_groups_data_1.json()['treeName'])
                            elif res_groups_data_1.json()['type'] == "group":
                                for device_group_2 in res_groups_data_1.json()['deviceExtendedInfo']['firewallsInGroup']:
                                    res_groups_data_2 = requests.get(f"https://fwaas.mhf.mhc/afa/api/v1/device/{device_group_2}", headers=headers, verify=False)
                                    
                                    if res_groups_data_2.json()['type'] == "firewall":
                                        devices.append(res_groups_data_2.json()['treeName'])
                                    elif res_groups_data_2.json()['type'] == "group":
                                        print("More loops needed")
                                    else:
                                        print("No data found")
                            else:
                                print("No data found")
                    else:
                        print("No data found")
                return report_name          
        else:
            print("Login failed")
    except Exception as e:
        print(f"Error: {e}")



# Example usage of login function
username_ = "svc_api"
password_ = "Test123!"
report_name = fetch_devices(username_, password_)
print("report: ", report_name)

# with open('devices.json','w') as f:
#     json.dump(devices,f,indent=2)

def remove_duplicates(devices):
    # Convert the list to a set to remove duplicates, then back to a list
    return list(set(devices))
unique_list = remove_duplicates(devices)
print(unique_list)
with open ('unique_devices.json','w') as f:
      json.dump(unique_list,f,indent=2)

with open ('unique_devices.json','r') as f1:
    data = json.load(f1)




def login(username, password):
    url = "https://fwaas.mhf.mhc/fa/server/connection/login"
    payload = json.dumps({"username": username, "password": password})
    headers = {'Content-Type': 'application/json'}
    try:
        response = requests.post(url, headers=headers, data=payload, verify=False)
        res_login_status = response.json().get('status')
        res_login = response.json()
        if res_login_status:
            print("Logged In Successfully")
            return res_login.get('SessionID')
        else:
            print("Login failed")
            return None
    except requests.exceptions.RequestException as e:
        print("An error occurred:", e)
        return None

def fetch_device_compliance(session_id, device):
    url = f'https://fwaas.mhf.mhc/afa/api/v1/baseline_compliance?device={device}'
    headers = {'Cookie': f'{session_id}; PHPSESSID={session_id}'}
    try:
        compliance_data = requests.get(url, headers=headers, verify=False)
        if compliance_data.status_code == 200:
            compliance_json = compliance_data.json()
            if compliance_json["profile"] == "FortiGateProfile":
                device_id = compliance_json['device']
                profile = compliance_json['profile']
                date = compliance_json['date']
                baseline_compliance_score = compliance_json['baseline_compliance_score']
                passed_requirement_count = compliance_json['passed_requirement_count']
                failed_requirement_count = compliance_json['failed_requirement_count']
                risks = []
                for names in compliance_json['requirements']:
                    name = names['name']
                    status = 'Manual Verification required' if names['status'] == "UNKNOWN" else names['status']
                    id = names['id']
                    rating = ratings.get(name)
                    risks_data = {
                        "Risk_Name": name,
                        "Risk_rating": rating,
                        "Risk_status": status,
                        "Risk_id": id
                    }
                    risks.append(risks_data)
                return {
                    "device": device_id,
                    
                   
                    "baseline_compliance_score": baseline_compliance_score,
                    "passed_requirement_count": passed_requirement_count,
                    "failed_requirement_count": failed_requirement_count,
                    "Profile": profile,
                    "Risks": risks
                }
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching compliance data for device {device}: {e}")
        return None

def load_existing_data(json_file_path):
    if os.path.exists(json_file_path):
        with open(json_file_path, 'r', encoding='utf-8') as jsonfile:
            data = json.load(jsonfile)
            print(f"Loaded existing data: {data}")  # Debug statement
            return data.get("data", [])
    return []

def save_data(json_file_path, data):
    with open(json_file_path, 'w', encoding='utf-8') as jsonfile:
        report = {
            "data": data
        }
        json.dump(report, jsonfile, indent=2)

def save_summary(summary_file_path, average_score, run_date):
    summary_entry = {
        "average_baseline_compliance_score": average_score,
        "run_date": run_date
    }
    if os.path.exists(summary_file_path):
        with open(summary_file_path, 'r+') as summary_file:
            summary_data = json.load(summary_file)
            summary_data.append(summary_entry)
            summary_file.seek(0)
            json.dump(summary_data, summary_file, indent=4)
    else:
        with open(summary_file_path, 'w') as summary_file:
            json.dump([summary_entry], summary_file, indent=4)

def calculate_average_score(data):
    scores = [record['baseline_compliance_score'] for record in data if 'baseline_compliance_score' in record]
    return sum(scores) / len(scores) if scores else 0

# Main script execution
if __name__ == "__main__":
    with open('unique_devices.json', 'r') as f:
        devices = json.load(f)

    username = "svc_api"
    password = "Test123!"
    session_id = login(username, password)
    compliance_algosec_data = []

    if session_id:
        # with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        #     future_to_device = {executor.submit(fetch_device_compliance, session_id, device): device for device in devices}
        #     for future in concurrent.futures.as_completed(future_to_device):
        #         result = future.result()
        #         if result:
        #             compliance_algosec_data.append(result)
        for device in devices:

            result = fetch_device_compliance(session_id, device)
            compliance_algosec_data.append(result)
            
            

             

        current_date = datetime.now().strftime('%Y-%m-%d')
        json_file_name = 'algosec_report.json'
        summary_file_name = 'compliance_summary.json'

        # Load existing data
        existing_data = load_existing_data(json_file_name)

        # Update the data with new entries
        updated_data = existing_data + compliance_algosec_data

        # Calculate the new average score
        current_avg_score = calculate_average_score(updated_data)
        print(current_avg_score)
        print(f"Calculated current average score: {current_avg_score}")  # Debug statement

        # Save the updated data in algosec_report.json
        save_data(json_file_name, updated_data)

        # Save the summary statistics in compliance_summary.json
        save_summary(summary_file_name, current_avg_score, current_date)

        print(f"Process completed. JSON files have been updated and saved as '{json_file_name}' and '{summary_file_name}'.")

# Load the JSON data
with open('algosec_report.json') as f:
    data = json.load(f)
for element in data['data']:
    element['average_baseline_score'] = current_avg_score
    element['report_name'] = report_name
with open('algosec_report.json','w') as f1:
    json.dump(data, f1, indent=4)
    

# Function to flatten the JSON
def flatten_json(y):
    out = []

    def flatten(x, name='', result=None):
        if result is None:
            result = {}
        if isinstance(x, dict):
            for a in x:
                flatten(x[a], name + a + '_', result)
        elif isinstance(x, list):
            i = 0
            for a in x:
                flatten(a, name + str(i) + '_', result)
                i += 1
        else:
            result[name[:-1]] = x
        return result

    for item in y['data']:
        flattened_item = flatten(item)
        out.append(flattened_item)
    
    return out

# Flatten the JSON data
flattened_data = flatten_json(data)

with open('algosec_report_flattened.json', 'w') as f8:
    json.dump(flattened_data, f8, indent=4)

# Convert the flattened data to a DataFrame
df = pd.DataFrame(flattened_data)

# Save the DataFrame to a CSV file
df.to_csv('algosec_report_flattened.csv', index=False)
print(report_name)