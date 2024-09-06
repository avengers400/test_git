import json
import requests
import datetime
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
            print(device)
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