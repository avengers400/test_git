import json

# Read the JSON data from the file
with open('dts_wiz_rule_names_ids.json', 'r') as json_file:
    data = json.load(json_file)


with open('unique_dts_vmss_rule_names_ids.json', 'r') as file:
    data1 = json.load(file)
dts_vmss_rule_names_ids_updated = []
for item in data:
   b = item['dts_vmss_rule_name']
   
   for items in data1:
    
        if items['value'] == b:
           dts_vmss_rule_names_ids_updated.append({"dts_vmss_rule_name": b ,"dts_vmss_rule_id": items['matched key']})
        else:
            print("Key not found")
print(len(dts_vmss_rule_names_ids_updated))
with open("dts_suppressed_vmss_rule_names_ids.json", "w") as json_final:
   json.dump(dts_vmss_rule_names_ids_updated,json_final,indent=4)