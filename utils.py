import json


def savejson(output_file,data, mode = 'w'):
    with open(output_file, mode, encoding='utf-8') as output:
        json.dump(data, output, indent=4, ensure_ascii=False)