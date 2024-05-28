import json

# Read the JSON data from the file
with open('matched_dts_wiz_vmss_rule_names.json', 'r') as json_file:
    data = json.load(json_file)


with open('final_result.json', 'r') as file:
    data1 = json.load(file)
dts_wiz_rule_names_ids = []
for item in data:
   b = item['dts_wiz_rule']
   
   for items in data1:
    
        if items['rule_name'] == b:
           dts_wiz_rule_names_ids.append({"dts_vmss_rule_name": item['dts_vmss_rule'] ,"dts_wiz_rule_name": items['rule_name'], "dts_wiz_rule_id": items['rule_id']})
        else:
            print("Key not found")
print(len(dts_wiz_rule_names_ids))
with open("dts_wiz_rule_names_ids.json", "w") as json_final:
   json.dump(dts_wiz_rule_names_ids,json_final,indent=4)