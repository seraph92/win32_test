import json

temp = {}


class Config(dict):
    def __init__(self, file_path="./config.json", *arg, **kw):
        super(Config, self).__init__(*arg, **kw)
        self.file_path = file_path
        print(f"file_path = [{self.file_path}]")
        self.reload(self.file_path)

    def __setitem__(self, key, item):
        self.__dict__[key] = item

    def __getitem__(self, key):
        return self.__dict__[key]

    def __repr__(self):
        return repr(self.__dict__)

    def __len__(self):
        return len(self.__dict__)

    def __delitem__(self, key):
        del self.__dict__[key]

    def clear(self):
        return self.__dict__.clear()

    def copy(self):
        return self.__dict__.copy()

    def has_key(self, k):
        return k in self.__dict__

    def update(self, *args, **kwargs):
        return self.__dict__.update(*args, **kwargs)

    def keys(self):
        return self.__dict__.keys()

    def values(self):
        return self.__dict__.values()

    def items(self):
        return self.__dict__.items()

    def pop(self, *args):
        return self.__dict__.pop(*args)

    def __cmp__(self, dict_):
        return self.__cmp__(self.__dict__, dict_)

    def __contains__(self, item):
        return item in self.__dict__

    def __iter__(self):
        return iter(self.__dict__)

    def __unicode__(self):
        return unicode(repr(self.__dict__))

    def reload(self, file_path):
        self.clear()
        print(f"file_path = [{file_path}]")
        if file_path:
            try:
                with open(file_path, "r") as f:
                    self.update(json.load(f))
            except FileNotFoundError as fe:
                print(f"error = [{fe}]")

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
    def update_each(self, data, var=None):
        if var == None:
            var = self.values

        for (k, v) in data.items():
            if isinstance(v, dict):
                self.update_each(v, var[k])
            else:
                var[k] = v

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


CONFIG = Config()

if __name__ == "__main__":
    conf = Config()
    #print(f"user_id = [{conf['user_id']}]")

    conf.values = {
        "user_id": "seraph92",
        "user_pw": "123456",
        "options": {
            "option1": "op_value1",
            "option2": "op_value2",
        },
    }
    conf.update_each({"options": {"add_key": "add_value"}})

    conf.export()