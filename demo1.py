import json

# Read the JSON data from the file
with open('unique_dts_vmss_rule_names.json', 'r') as json_file:
    data = json.load(json_file)


with open('WIZ-VMSS-RULES.json', 'r') as file:
    data1 = json.load(file)
dts_final_data = []
for item in data:
   b = item['value']
   print(b)
   for items in data1:
    for key in items.keys():
        if b == key:
           dts_final_data.append({"dts_vmss_rule": key, "dts_wiz_rule": items[key]})
        else:
            print("Key not found")
print(len(dts_final_data))
with open("matched_dts_wiz_vmss_rule_names.json", "w") as json_final:
   json.dump(dts_final_data,json_final,indent=4)