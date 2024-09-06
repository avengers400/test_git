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
# devices = []
# report_name = ''

# def fetch_devices(username_, password_):
#     url = "https://fwaas.mhf.mhc/fa/server/connection/login"

#     payload = json.dumps({
#         "username": username_,
#         "password": password_
#     })
#     headers = {
#         'Content-Type': 'application/json'
#     }

#     try:
#         response = requests.request("POST", url, headers=headers, data=payload, verify=False)
#         res_login_status = response.json()['status']
        
#         res_login = response.json()

#         if res_login_status:
#             print("Logged In Successfully")
#             if 'SessionID' in res_login:
#                 res_login_sessionId = res_login['SessionID']
#                 headers = {
#                     'Cookie': f'{res_login_sessionId}; PHPSESSID={res_login_sessionId}'
#                 }

#                 res_firewall_groups = requests.get("https://fwaas.mhf.mhc/afa/api/v1/device/FW", headers=headers, verify=False)
#                 report_name=res_firewall_groups.json()['lastReport']

#                 for group in res_firewall_groups.json()['deviceExtendedInfo']['firewallsInGroup']:
#                     res_device_firewall_groups = requests.get(f'https://fwaas.mhf.mhc/afa/api/v1/device/{group}', headers=headers, verify=False)
                    
#                     if res_device_firewall_groups.json()['type'] == "firewall":
#                         devices.append(res_device_firewall_groups.json()['displayName'])
#                     elif res_device_firewall_groups.json()['type'] == "group":
#                         for device_group_1 in res_device_firewall_groups.json()['deviceExtendedInfo']['firewallsInGroup']:
#                             res_groups_data_1 = requests.get(f"https://fwaas.mhf.mhc/afa/api/v1/device/{device_group_1}", headers=headers, verify=False)
                            
#                             if res_groups_data_1.json()['type'] == "firewall":
#                                 devices.append(res_groups_data_1.json()['displayName'])
#                             elif res_groups_data_1.json()['type'] == "group":
#                                 for device_group_2 in res_groups_data_1.json()['deviceExtendedInfo']['firewallsInGroup']:
#                                     res_groups_data_2 = requests.get(f"https://fwaas.mhf.mhc/afa/api/v1/device/{device_group_2}", headers=headers, verify=False)
                                    
#                                     if res_groups_data_2.json()['type'] == "firewall":
#                                         devices.append(res_groups_data_2.json()['displayName'])
#                                     elif res_groups_data_2.json()['type'] == "group":
#                                         print("More loops needed")
#                                     else:
#                                         print("No data found")
#                             else:
#                                 print("No data found")
#                     else:
#                         print("No data found")
#                 return report_name          
#         else:
#             print("Login failed")
#     except Exception as e:
#         print(f"Error: {e}")



# # Example usage of login function
# username_ = "svc_api"
# password_ = "Test123!"
# report_name = fetch_devices(username_, password_)
# print("report: ", report_name)

# # with open('devices.json','w') as f:
# #     json.dump(devices,f,indent=2)

# def remove_duplicates(devices):
#     # Convert the list to a set to remove duplicates, then back to a list
#     return list(set(devices))
# unique_list = remove_duplicates(devices)
# print(unique_list)
# with open ('unique_devices.json','w') as f:
#       json.dump(unique_list,f,indent=2)

# with open ('unique_devices.json','r') as f1:
#     data = json.load(f1)




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
a = []
def fetch_device_compliance(session_id, device):
   
    url = f'https://fwaas.mhf.mhc/afa/api/v1/baseline_compliance?device={device}'
    headers = {'Cookie': f'{session_id}; PHPSESSID={session_id}'}
    try:
        compliance_data = requests.get(url, headers=headers, verify=False)
        if compliance_data.status_code == 200:
            compliance_json = compliance_data.json()
            #if compliance_json["profile"] == "FortiGateProfile":
            device_id = compliance_json['device']
            a.append(device_id)
                
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching compliance data for device {device}: {e}")
        return None
username = "svc_api"
password = "Test123!"
session_id = login(username, password)
print(session_id)
with open('unique_devices.json','r') as f:
    data = json.load(f)
for i in data:
    fetch_device_compliance(session_id,i)
with open('devices_compliants_report_count_all.json', 'w') as f1:
    json.dump(a,f1,indent=2)