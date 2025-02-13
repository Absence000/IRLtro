import json

def openjson(filename):
    with open(f"jsonFiles/{filename}.json") as file:
        return json.load(file)

def savejson(filename, data):
    with open(f"jsonFiles/{filename}.json", "w") as file:
        json.dump(data, file, indent=4)
