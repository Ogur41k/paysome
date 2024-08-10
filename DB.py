import json


def load() -> list:
    with open("DB.json", "r") as f:
        return json.load(f)["data"]


def save(data: list):
    with open("DB.json", "w") as f:
        json.dump({"data": data}, f)


def add(content: list):
    save(load() + [content])


def delete(name: str):
    data = load()
    for i in data:
        if i["name"] == name:
            data.remove(i)
            break
    save(data)


def get(name: str) -> dict:
    data = load()
    for d in data:
        if d["name"] == name:
            return d
    return 404


def get_names() -> list:
    return [d["name"] for d in load()]
