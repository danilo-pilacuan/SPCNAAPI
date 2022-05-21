#Actual script
import socket
import sys
import json
import time
import os
from flask_cors import CORS
import signal
import shlex, subprocess
import re
import requests

#No olvidar analizar con regex que mandar y que no desde latex al texToEs

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

    ####print("Type:",type(data))

    for key,value in data.items():
        scriptTxt=scriptTxt.replace(value,data_abs[key])
    
    return scriptTxt

# def wrapScriptEntrada(expresiones):
#     expWrapped=[];
#     for exp in expresiones:
#         buscarNoW=re.findall(r"\d+[\+\-\*/\^]\d",exp)
#         if buscarNoW!=NULL:
#             expWrapped.append("tex("+exp+");")
#         else:
            
#             pass
#     return expWrapped
def wrapScriptEntrada(expresiones):
    expWrapped=[];
    for exp in expresiones:
        buscarNoTex=re.findall(r"^\d+[\+\-\*/\^]\d",exp)
        print("zzzzzzzzzzzzzzzzzzzzzzzzz")
        print(exp)
        print(buscarNoTex)
        if len(buscarNoTex):
            expWrapped.append("tex(\""+exp+"\");")
        else:
            expWrapped.append("tex("+exp+");")
        
    print("vvvvvvvvvvvvvvvvvvvvvvv")
    print(expWrapped)
    return expWrapped

def wrapScript(expresiones):
    expWrapped=[];
    for exp in expresiones:
        expWrapped.append("tex("+exp+");")
    return expWrapped

def procesarMaxima(expresiones):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('localhost', maximaPort)
    ###print('starting up on {} port {}'.format(*server_address))
    sock.bind(('',0))

    portNumber=sock.getsockname()[1]
    # Listen for incoming connections
    sock.listen(1)
    cont = 0
    aux = 0
    respuesta = ""
    maximapid = os.spawnlp(os.P_NOWAIT,"maxima","maxima","--server=" + str(portNumber))
    ###print('waiting for a connection')
    connection, client_address = sock.accept()
    connection.settimeout(0.1)
    ###print('connection from', client_address)
    cont2=0
    respuesta = ""
    for expresion in expresiones:
        cont = 0
        aux = 0
        try:
            while aux!=1:  
                try:
                    if expresion=="tex();":
                        ###print("No va a valer")
                        aux=1
                        continue
                    ###print("Sending "+ expresion+"\n")
                    connection.sendall(str.encode(expresion+"\n"))
                    # Receive the data in small chunks and retransmit it
                    aux2=1
                    while aux2==1:
                        aux=1
                        data = connection.recv(1024)
                        #####print('received {!r}'.format(data))
                        respuesta = respuesta + data.decode("utf-8") 
                        #####print("Data")
                        if not data:
                            #####print('no data from', client_address)
                            aux2=0
                            break
                        else:
                            #####print('sending data back to the client')
                            #my_str = request.GET["cadena"]
                            #my_str_as_bytes = str.encode(my_str)
                            #type(my_str_as_bytes) # ensure it is byte representation
                            #connection.sendall(b'tex(solve([x+y+z=5,3*x-5*y=10,y+2*z=3],[x,y,z]));')
                            #input("ingrese algo")
                            cont = cont +1
                            aux=1
                except Exception as e:
                    
                    #connection.close()
                    ####print("Excepcion: ")
                    ####print(e)
                    aux=1
                finally:
                    # Clean up the connection
                    ###print("Cerrado")
                    pass
                    #connection.close()
                    #time.sleep(3)
        except Exception as e:
            ###print(e)
            pass
        finally:
            #####print("Llegado: "+str(cont2+1)+" veces")
            cont2=cont2+1
            # salida = respuesta.split("(%i1) ")pass
            # salida = salida[1].split("(%o1)")
            # salida=salida[0].replace("\n","")
            ####print(respuesta)
            #return jsonify(salida)
    connection.close()
    return respuesta

def procesarMaximaEntrada(expresiones):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('localhost', maximaPort)
    ###print('starting up on {} port {}'.format(*server_address))
    sock.bind(('',0))

    portNumber=sock.getsockname()[1]
    # Listen for incoming connections
    sock.listen(1)
    cont = 0
    aux = 0
    respuesta = ""
    maximapid = os.spawnlp(os.P_NOWAIT,"maxima","maxima","--server=" + str(portNumber))
    ###print('waiting for a connection')
    connection, client_address = sock.accept()
    connection.settimeout(0.1)
    ###print('connection from', client_address)
    cont2=0
    respuesta = ""
    for expresion in expresiones:
        cont = 0
        aux = 0
        try:
            while aux!=1:  
                try:
                    print(",,,,,,,,,,,,,,,,,,,,,")
                    print(expresion)
                    if expresion=="tex();":
                        ###print("No va a valer")
                        aux=1
                        continue
                    #input()
                    buscarNoTex=re.findall(r"^\d+[\+\-\*/\^]\d",expresion)
                    
                    ###print("Sending "+ expresion+"\n")
                    connection.sendall(str.encode(expresion+"\n"))
                    # Receive the data in small chunks and retransmit it
                    aux2=1
                    while aux2==1:
                        aux=1
                        data = connection.recv(1024)
                        #####print('received {!r}'.format(data))
                        respuesta = respuesta + data.decode("utf-8") 
                        #####print("Data")
                        if not data:
                            #####print('no data from', client_address)
                            aux2=0
                            break
                        else:
                            #####print('sending data back to the client')
                            #my_str = request.GET["cadena"]
                            #my_str_as_bytes = str.encode(my_str)
                            #type(my_str_as_bytes) # ensure it is byte representation
                            #connection.sendall(b'tex(solve([x+y+z=5,3*x-5*y=10,y+2*z=3],[x,y,z]));')
                            #input("ingrese algo")
                            cont = cont +1
                            aux=1
                except Exception as e:
                    
                    #connection.close()
                    ####print("Excepcion: ")
                    ####print(e)
                    aux=1
                finally:
                    # Clean up the connection
                    ###print("Cerrado")
                    pass
                    #connection.close()
                    #time.sleep(3)
        except Exception as e:
            ###print(e)
            pass
        finally:
            #####print("Llegado: "+str(cont2+1)+" veces")
            cont2=cont2+1
            # salida = respuesta.split("(%i1) ")pass
            # salida = salida[1].split("(%o1)")
            # salida=salida[0].replace("\n","")
            ####print(respuesta)
            #return jsonify(salida)
    connection.close()
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    print(respuesta)
    return respuesta

def regexMetadataEliminarMaxima(entrada):
    respuestaReg=re.sub(r"pid=\d+\n.*\n.*\n.*\n.*\n.*\n","",entrada)    
    ###print("RespuestaReg:")
    ###print(respuestaReg)
    listaRespuestas=re.findall(r"^\(%i\d+\).+?(?=\([%])",respuestaReg, re.MULTILINE | re.DOTALL | re.UNICODE)
    for i in range(0,len(listaRespuestas)):
        ###print("sdaas")
        listaRespuestas[i]=re.sub(r"^\(%[io]\d+\)\s","",listaRespuestas[i])
        listaRespuestas[i]=listaRespuestas[i].replace("\n","")
    return listaRespuestas

def echoEntrada(entrada):
    salida=[]
    for linea in entrada:
        buscarNoTex=re.findall(r"^\d+[\+\-\*/\^]\d",linea)
        print("qqqqqqqqqqqqqqqqqqqqqqqqqq")
        print(linea)
        print(buscarNoTex)
        if len(buscarNoTex):
            salida.append(linea)
        else:
            envoltorios=obtenerEnvoltorios(linea)
            auxLinea=linea
            print("222222222222222222222222222222222222222")
            print(envoltorios)

            for grupo in envoltorios:
                for envoltorio in grupo:
                    auxLinea=auxLinea.replace(envoltorio,"")            
            salida.append(auxLinea)
    print("222222222222222222222222222222222222222")
    print(salida)
    return salida

def obtenerEnvoltorios(entrada):
    respuestaEnv=re.findall(r"(^.*\()|(.$)|(,.*\))",entrada)
    ###print("respuestaEnv")
    ###print(respuestaEnv)
    return respuestaEnv

def latexToEs(entrada):
    latexTxt  = entrada
    url = 'http://localhost:8080/snuggle/procesarLatex'
    myobj = {'entrada': latexTxt}

    response = requests.post(url, json = myobj)
    salida=response.json()
    cmathml=salida['salida']

    result = subprocess.run(['python2', 'module.py' ,'--cmathml',cmathml], stdout=subprocess.PIPE)

    respuesta=result.stdout.decode("utf-8")
    return respuesta

def salidaToSpeech(entrada):
    salida=[]
    for i in range(0,len(entrada)):
        #\d+[\+\-\*/\^]\d
        auxSalidaSpeech=""
        buscarNoTexToEs=re.findall(r"\$\$.?\$\$",entrada[i])
        print("**************")
        print(entrada[i])
        print(buscarNoTexToEs)
        if not len(buscarNoTexToEs):
            auxSalidaSpeech=latexToEs(entrada[i])
            print("/////////")
        else:
            print("?????????????")
            auxSalidaSpeech=entrada[i].replace("$$","")

        ###print("-------------------------------")
        ###print(auxSalidaSpeech)
        auxSalidaSpeech=re.sub(r"->.*\n","",auxSalidaSpeech)
        ###print("++++++++++++++++++++")
        ###print(auxSalidaSpeech)
        auxSalidaSpeech=auxSalidaSpeech.replace("la lista de","el valor de")
        ###print(auxSalidaSpeech)
        salida.append(auxSalidaSpeech)
    return salida

def echoToSpeech(entrada,entradaNoEcho):
    print("EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE")
    print(entrada)
    salida=[]
    for i in range(0,len(entrada)):
        #buscarNoTexToEs=re
        auxSalidaSpeech=latexToEs(entrada[i])
        ###print("-------------------------------")
        ###print(auxSalidaSpeech)
        auxSalidaSpeech=re.sub(r"->.*\n","",auxSalidaSpeech)
        entradaNoEnv=re.sub(r"(^.*\()|(.$)|(,.*\))","",entradaNoEcho[i])
        ###print("++++++++++++++++++++")
        ###print(auxSalidaSpeech)
        salidaSpeech=entradaNoEcho[i].replace(entradaNoEnv,auxSalidaSpeech)
        
        salida.append(salidaSpeech)
    return salida

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

        scriptTxt  = request.form.get('scriptTxt')
        print("¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿")
        print(scriptTxt)
        scriptTxt=translateScript(scriptTxt)
        scriptTxt=scriptTxt+"\n"
        scriptTxt=scriptTxt.replace("\r","")
        expresiones=scriptTxt.split("\n")
        entradaNoEcho=expresiones[:-1]
        start_time = time.time()
        echoExpresiones=echoEntrada(expresiones)
        print("1--- %s seconds ---" % (time.time() - start_time))
        
        ###print("scriptTxtTranslated")
        ###print(expresiones)
        expresiones=wrapScript(expresiones)
        
        echoExpresiones=wrapScriptEntrada(echoExpresiones)
        ###print("Expresiones script")
        ###print(expresiones)
        ###print("echoExpresiones script")
        ###print(echoExpresiones)
        
        start_time = time.time()
        
        respuesta=procesarMaxima(expresiones)
        print("2--- %s seconds ---" % (time.time() - start_time))
        start_time = time.time()
        respuestaEchoEntrada=procesarMaximaEntrada(echoExpresiones)
        print("3--- %s seconds ---" % (time.time() - start_time))
        ###print("Respuesta no reg:")
        ###print(respuesta)
        start_time = time.time()
        listaRespuestas=regexMetadataEliminarMaxima(respuesta)
        print("4--- %s seconds ---" % (time.time() - start_time))
        start_time = time.time()
        lrEchoEntrada=regexMetadataEliminarMaxima(respuestaEchoEntrada)
        print("5--- %s seconds ---" % (time.time() - start_time))
        start_time = time.time()
        echoSpeech=echoToSpeech(lrEchoEntrada,entradaNoEcho)
        print("6--- %s seconds ---" % (time.time() - start_time))
        ###print("ListaRespuestas: ")
        ###print(listaRespuestas)
        salidaSpeech=salidaToSpeech(listaRespuestas)
        
        respuestaJson={"entradaScript":entradaNoEcho,"salida":listaRespuestas,"entradaSpeech":echoSpeech,"salidaSpeech":salidaSpeech}

        #incluir speechLatex entradas y speechLatexSalidas usando procesarLatex
        ###print("respuestaJson")
        ###print(respuestaJson)

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

        ###print(latexTxt)
        url = 'http://localhost:8080/snuggle/procesarLatex'
        myobj = {'entrada': latexTxt}

        response = requests.post(url, json = myobj)
        salida=response.json()
        cmathml=salida['salida']

        ###print(cmathml)

        result = subprocess.run(['python2', 'module.py' ,'--cmathml',cmathml], stdout=subprocess.PIPE)
        ###print(result.stdout)


        respuesta=str(result.stdout)
        ###print(respuesta)

        

        respuestaJson={"salidas":respuesta}
        #####print("pid="+str(maximapid))
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
        #####print("pid="+str(maximapid))
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

