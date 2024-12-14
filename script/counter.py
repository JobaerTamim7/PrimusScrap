from os import walk
from json import load

def count_contents(path : str):
    info_dict = {}
    for root, dirs, files in walk(path):

        for file in files:
            with open(f"{root}/{file}", "r") as f:
                data = load(f)
                info_dict[str(file)] = len(data)
            
    with open("../info.json", "w") as f:
        f.write(str(info_dict))
                    

if __name__ == "__main__":
    count_contents("../data/json_pool")
                