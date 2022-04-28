import requests
import subprocess

url = 'http://localhost:8080/snuggle/createPerson'
myobj = {'entrada': '$$ \\frac{2x-y^2}{\\sin xy(x-4)} $$'}

response = requests.post(url, json = myobj)
salida=response.json()
cmathml=salida['salida']

#print(cmathml)

result = subprocess.run(['python2', 'module.py' ,'--cmathml',cmathml], stdout=subprocess.PIPE)
print(result.stdout)