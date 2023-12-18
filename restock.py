import glob
import json
number = 5
def get_json_data(file):
    with open(file, "r") as json_file:
        json_data=json.load(json_file)
    return json_data

def write_json_data(file,data):
    with open(file, "w") as json_file:
        dictionary=json.dumps(data,indent=4)
        json_file.write(dictionary)


for file_json in glob.glob("Item_Data" + "/*"):
    # load a json file 
    data = get_json_data(file_json)
    for item_data in data["Items"]:
        item_data["Item_Stock"] = number
    write_json_data(file_json,data)
        