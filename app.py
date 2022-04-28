import socket
import sys
import json
import time
import os
from flask_cors import CORS
import signal
import shlex, subprocess

import requests



from flask import Flask, jsonify,request,make_response
maximaPort=10000
serverPort=8000
app = Flask(__name__)
CORS(app)

def translateScript(scriptTxt):
    json_file = open("localization/es.json")
    data = json.load(json_file)

    json_abs_file = open("localization/absolute.json")
    data_abs = json.load(json_abs_file)

    #print("Type:",type(data))

    for key,value in data.items():
        scriptTxt=scriptTxt.replace(value,data_abs[key])
    
    return scriptTxt

def wrapScript(expresiones):
    expWrapped=[];
    for exp in expresiones:
        expWrapped.append("tex("+exp+");")
    return expWrapped

@app.route('/ping')
def ping():
    return "Hello world"

@app.route('/analizarSintaxisExpr')
def analizarSintaxis():
    #analizar una a una las expresiones por medio del uso de regexp
    pass

@app.route('/procesarScript', methods=['GET', 'POST'])
def procesar():
    if request.method == 'POST':
        #email = request.form.get('email')
        #return request.args.get("user")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = ('localhost', maximaPort)
        print('starting up on {} port {}'.format(*server_address))
        sock.bind(('',0))

        portNumber=sock.getsockname()[1]
        # Listen for incoming connections
        sock.listen(1)

        cont = 0
        aux = 0
        respuesta = ""
        
        maximapid = os.spawnlp(os.P_NOWAIT,"maxima","maxima","--server=" + str(portNumber))
        #print("scriptTxt="+request.GET["scriptTxt"])
        #scriptTxt = request.args.get("scriptTxt");
        scriptTxt  = request.form.get('scriptTxt')

        scriptTxt = scriptTxt.replace("%28","(")
        scriptTxt = scriptTxt.replace("%21","!")
        scriptTxt = scriptTxt.replace("%2A","*")
        #scriptTxt = scriptTxt.replace("%27\'","")
        scriptTxt = scriptTxt.replace("%28","(")
        scriptTxt = scriptTxt.replace("%29",")")
        scriptTxt = scriptTxt.replace("%3B",";")
        scriptTxt = scriptTxt.replace("%3A",":")
        scriptTxt = scriptTxt.replace("%40","@")
        scriptTxt = scriptTxt.replace("%26","&")
        scriptTxt = scriptTxt.replace("%3D","=")
        scriptTxt = scriptTxt.replace("%2B","+")
        scriptTxt = scriptTxt.replace("%24","$")
        scriptTxt = scriptTxt.replace("%2C",",")
        scriptTxt = scriptTxt.replace("%2F","/")
        scriptTxt = scriptTxt.replace("%3F","?")
        scriptTxt = scriptTxt.replace("%25","%")
        scriptTxt = scriptTxt.replace("%23","#")
        scriptTxt = scriptTxt.replace("%5B","[")
        scriptTxt = scriptTxt.replace("%5D","]")
        scriptTxt = scriptTxt.replace("%5E","^")

        scriptTxt=translateScript(scriptTxt)
        scriptTxt=scriptTxt+"\n"
        #print("scriptTxt="+scriptTxt)
        expresiones=scriptTxt.split("\n")
        print(expresiones)
        expresiones=wrapScript(expresiones)
        print(expresiones)
        
        print('waiting for a connection')
        connection, client_address = sock.accept()
        #connection.settimeout(0.025) #timeout mas bajo mas posiblemente exacto
        connection.settimeout(0.1)
        print('connection from', client_address)
        cont2=0
        respuesta = ""
        for expresion in expresiones:
            #por cada expresion llamar a procesar latex y crear una variable al array como salida o llamar al api snuggle desde aqui mismo
            cont = 0
            aux = 0
            try:
                while aux!=1:  
                    try:
                        if expresion=="tex();":
                            print("No va a valer")
                            aux=1
                            continue
                        print("Sending "+ expresion+"\n")
                        
                        connection.sendall(str.encode(expresion+"\n"))
                        # Receive the data in small chunks and retransmit it
                        aux2=1
                        while aux2==1:
                            aux=1
                            data = connection.recv(1024)
                            ##print('received {!r}'.format(data))
                            respuesta = respuesta + data.decode("utf-8") 
                            ##print("Data")
                            if not data:
                                ##print('no data from', client_address)
                                aux2=0
                                break
                            else:
                                ##print('sending data back to the client')
                                #my_str = request.GET["cadena"]
                                #my_str_as_bytes = str.encode(my_str)
                                #type(my_str_as_bytes) # ensure it is byte representation
                                #connection.sendall(b'tex(solve([x+y+z=5,3*x-5*y=10,y+2*z=3],[x,y,z]));')
                                #input("ingrese algo")
                                cont = cont +1
                                aux=1
                    except Exception as e:
                        
                        #connection.close()
                        #print("Excepcion: ")
                        #print(e)
                        aux=1
                    finally:
                        # Clean up the connection
                        print("Cerrado")
                        #connection.close()
                        #time.sleep(3)
            except Exception as e:
                print(e)
            finally:
                ##print("Llegado: "+str(cont2+1)+" veces")
                cont2=cont2+1
                # salida = respuesta.split("(%i1) ")pass
                # salida = salida[1].split("(%o1)")
                # salida=salida[0].replace("\n","")
                #print(respuesta)
                #return jsonify(salida)
                
        connection.close()
        print(respuesta)
        respuestaJson={"message":respuesta}
        ##print("pid="+str(maximapid))
        response = make_response(
            jsonify(
                respuestaJson
            ),
            200,
        )
        response.headers["Content-Type"] = "application/json"
        return response
    else:
        pass

@app.route('/procesarLatex', methods=['GET', 'POST'])
def procesarLatex():
    if request.method == 'POST':
        
        latexTxt  = request.form.get('latexTxt')

        print(latexTxt)
        url = 'http://localhost:8080/snuggle/procesarLatex'
        stringEntrada= '$$ \\frac{2x-y^2}{\\sin xy(x-4)} $$'
        print(stringEntrada)
        myobj = {'entrada': latexTxt}

        response = requests.post(url, json = myobj)
        salida=response.json()
        cmathml=salida['salida']

        print(cmathml)

        result = subprocess.run(['python2', 'module.py' ,'--cmathml',cmathml], stdout=subprocess.PIPE)
        print(result.stdout)


        respuesta=str(result.stdout)
        ##print(respuesta)
        respuestaJson={"message":respuesta}
        ##print("pid="+str(maximapid))
        response = make_response(
            jsonify(
                respuestaJson
            ),
            200,
        )
        response.headers["Content-Type"] = "application/json"
        return response
    else:
        pass

@app.route('/demorarEjecucion', methods=['GET', 'POST'])
def demorarEjecucion():
    if request.method == 'POST':
        
        tiempoMS  = request.form.get('tiempoMS')
        time.sleep(int(tiempoMS)/1000)
        respuestaJson={"message":"exito"}
        ##print("pid="+str(maximapid))
        response = make_response(
            jsonify(
                respuestaJson
            ),
            200,
        )
        response.headers["Content-Type"] = "application/json"
        return response
    else:
        pass


if __name__ == '__main__':
    app.run(debug=True, port=serverPort)

