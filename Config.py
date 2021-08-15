import json

temp = {}


class Config:
    def __init__(self, file_path="./config.json"):
        self.values = temp
        self.file_path = file_path
        self.reload()

    def reload(self):
        self.clear()
        if self.file_path:
            try:
                with open(self.file_path, "r") as f:
                    self.values.update(json.load(f))
            except FileNotFoundError as fe:
                print(f"error = [{fe}]")

    def clear(self):
        self.values.clear()

    """
    {
        "k1":"v1"
        "K2":{
            "K21":"v21"
        }
        "k3":[
            {
                "k31":"v31"
            },
            {
                "k32":"v32"
            }
 
        ]
    }
    """
    # config.values['test']['test2']['test3']
    def update(self, data, var=None):
        if var == None:
            var = self.values
        if isinstance(data, list):
            for i, v in enumerate(data):
                if isinstance(v, dict) or isinstance(v, list):
                    self.update(v)
                else:
                    var[i] = v
        elif isinstance(data, dict):
            for (k, v) in data.items():
                if isinstance(v, dict) or isinstance(v, list):
                    self.update(v)
                else:
                    var[k] = v
        else:
            var = data

    def update2(self, data):
        for (k1, v1) in data.items():
            if isinstance(v1, dict):
                for (k2, v2) in v1.items():
                    if isinstance(v2, dict):
                        for (k3, v3) in v2.items():
                            self.values[k1][k2][k3] = v3
                    else:
                        self.values[k1][k2] = v2
            else:
                self.values[k1] = v1

    def export(self, save_file_name="./config.json"):
        if save_file_name:
            with open(save_file_name, "w") as f:
                json.dump(dict(self.values), f)


if __name__ == "__main__":
    conf = Config()
    conf.values = {
        "user_id": "seraph92",
        "user_pw": "123456",
        "options": [
            {
                "option1": "op_value1",
                "option2": "op_value2",
            },
            {"option3": "op_value3"},
        ],
    }
    conf.update({"options": {"add_key": "add_value"}})

    conf.export()
