
import json
import requests
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
#                 print("result: ", res_firewall_groups.json().get('lastReport'))
#                 report_name = res_firewall_groups.json().get('lastReport')

                
#     except Exception as e:
#         print(f"Error: {e}")
#     return 

   

# # Example usage of login function
# username_ = "svc_api"
# password_ = "Test123!"
# fetch_devices(username_, password_)
# print(report_name)
# import json
# with open('algosec_report.json') as f:
#     data = json.load(f)
# if isinstance(data['data'], list) and all(isinstance(item, dict) for item in data['data']):
#     # Remove duplicates based on the entire dictionary
#     unique_data = [dict(t) for t in {tuple(sorted(d.items())) for d in data['data']}]

#     # Convert back to JSON if needed
#     unique_json_data = json.dumps({"data": unique_data}, indent=4)
#     print(unique_json_data)
# else:
#     print("Data is not in the expected format")
# def make_hashable(item):
#     if isinstance(item, dict):
#         return tuple(sorted((k, make_hashable(v)) for k, v in item.items()))
#     elif isinstance(item, list):
#         return tuple(make_hashable(x) for x in item)
#     else:
#         return item

# # Ensure the data is a list of dictionaries
# if isinstance(data['data'], list) and all(isinstance(item, dict) for item in data['data']):
#     # Remove duplicates based on the entire dictionary
#     unique_data = [dict(t) for t in {make_hashable(d) for d in data['data']}]

#     # Convert back to JSON if needed
#     unique_json_data = json.dumps({"data": unique_data}, indent=4)
#     print(len(unique_json_data))
# else:
#     print("Data is not in the expected format")
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
                print(report_name)
                for group in res_firewall_groups.json()['deviceExtendedInfo']['firewallsInGroup']:
                    res_device_firewall_groups = requests.get(f'https://fwaas.mhf.mhc/afa/api/v1/device/{group}', headers=headers, verify=False)
                    
                    if res_device_firewall_groups.json()['type'] == "firewall":
                        devices.append(res_device_firewall_groups.json()['treeName'])
                        print(res_device_firewall_groups.json()['treeName'])
                    elif res_device_firewall_groups.json()['type'] == "group":
                        for device_group_1 in res_device_firewall_groups.json()['deviceExtendedInfo']['firewallsInGroup']:
                            res_groups_data_1 = requests.get(f"https://fwaas.mhf.mhc/afa/api/v1/device/{device_group_1}", headers=headers, verify=False)
                            
                            if res_groups_data_1.json()['type'] == "firewall":
                                devices.append(res_groups_data_1.json()['treeName'])
                                print(res_groups_data_1.json()['treeName'])
                            elif res_groups_data_1.json()['type'] == "group":
                                for device_group_2 in res_groups_data_1.json()['deviceExtendedInfo']['firewallsInGroup']:
                                    res_groups_data_2 = requests.get(f"https://fwaas.mhf.mhc/afa/api/v1/device/{device_group_2}", headers=headers, verify=False)
                                    
                                    if res_groups_data_2.json()['type'] == "firewall":
                                        devices.append(res_groups_data_2.json()['treeName'])
                                        print(res_groups_data_2.json()['treeName'])
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
username_ = "svc_api"
password_ = "Test123!"
report_name = fetch_devices(username_, password_)
print("report: ", report_name)


