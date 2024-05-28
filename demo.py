import json

# Read the JSON data from the file
with open('dts_vmss_rule_names.json', 'r') as file:
    data = json.load(file)

# Use a dictionary to store unique key-value pairs
unique_data = {}
for entry in data:
    key = entry['matched key']
    value = entry['value']
    if key not in unique_data:
        unique_data[key] = value

# Convert the dictionary back to a list of dictionaries
unique_data_list = [{'matched key': key, 'value': value} for key, value in unique_data.items()]

# Write the unique key-value pairs back to a JSON file
with open('unique_dts_vmss_rule_names.json', 'w') as file:
    json.dump(unique_data_list, file, indent=4)

print("Unique key-value pairs have been written to unique_dts_vmss_rule_names.json")
