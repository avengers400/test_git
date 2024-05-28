import json

# Read the JSON data from the file
with open('dts_suppressed_vmss_rule_names_ids.json', 'r') as json_file:
    data = json.load(json_file)


with open('DTSS-VMSS-RULES_Accounts.json', 'r') as file:
    data1 = json.load(file)
dts_vmss_rule_names_ids_updated = []
for item in data:
   b = item['dts_vmss_rule_id']
   
   for items in data1:
    
        if items['CriteriaRules'] == b:
           dts_vmss_rule_names_ids_updated.append({"dts_vmss_rule_name": b ,"dts_vmss_cloud_accounts": items['Unique CriteriaCloudAccounts']})
        else:
            print("Key not found")
print(len(dts_vmss_rule_names_ids_updated))
with open("dts_suppressed_vmss_rule_ids_accounts.json", "w") as json_final:
   json.dump(dts_vmss_rule_names_ids_updated,json_final,indent=4)