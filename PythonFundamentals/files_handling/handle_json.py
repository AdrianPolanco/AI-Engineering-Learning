import json

with open("file.json", "w") as json_file:
    data = {
        "people": [
            {"name": "Adrian", "age": 24, "religion": "Atheist"},
            {"name": "Yarilyn", "age": 21, "religion": "Evangelical Christian"}
        ]
    }
    json.dump(data, json_file, indent=4)

with open("file.json", "r") as json_file:
    data = json.load(json_file)
    print(data)