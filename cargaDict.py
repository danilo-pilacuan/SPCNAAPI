import json
import re

scriptTxt="""resolver(x^2+4*x+4=0);
          factorar(x^2+4*x+4);
          residuo(25,4);"""

json_file = open("localization/es.json")
data = json.load(json_file)

json_abs_file = open("localization/absolute.json")
data_abs = json.load(json_abs_file)

#print("Type:",type(data))

for key,value in data.items():
    scriptTxt=re.sub(';','$',scriptTxt)

print(scriptTxt)