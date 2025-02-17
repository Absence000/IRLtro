import json

def openjson(filename, overwritePath=None):
    if overwritePath is not None:
        path = filename
    else:
        path = f"jsonFiles/{filename}.json"
    with open(path) as file:
        return json.load(file)

def savejson(filename, data, overwritePath=None):
    if overwritePath is not None:
        path = filename
    else:
        path = f"jsonFiles/{filename}.json"
    with open(path, "w") as file:
        json.dump(data, file, indent=4)
