from datetime import datetime
import json


def savejson(output_file,data, mode = 'w'):
    with open(output_file, mode, encoding='utf-8') as output:
        json.dump(data, output, indent=4, ensure_ascii=False)

def datetime_handler(obj):
  if isinstance(obj, datetime):
    return obj.isoformat()
  else:
    return obj
  
def datetime_decoder(obj, key):
  if key in obj:
    obj[key] = datetime.fromisoformat(obj[key])
  return obj