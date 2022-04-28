import socket
import sys
import json
import time
import os
from flask_cors import CORS
import signal
import shlex, subprocess

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
        sock.bind(server_address)

        # Listen for incoming connections
        sock.listen(1)

        cont = 0
        aux = 0
        respuesta = ""
        
        maximapid = os.spawnlp(os.P_NOWAIT,"maxima","maxima","--server=" + "10000")
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



        # scriptTxt = "tex(sum(f(i),i,0,m) * sum(g(j),j,0,n));\ntex(limit( sin(3*x)/x,  x,0));\n";
        # scriptTxt=scriptTxt+scriptTxt;
        # scriptTxt=scriptTxt+scriptTxt;
        # scriptTxt=scriptTxt+scriptTxt;
        # scriptTxt=scriptTxt+"for a:-3 thru 260000 step 7 do display(a);";
        # scriptTxt=scriptTxt+scriptTxt;
        # scriptTxt=scriptTxt+scriptTxt;
        # scriptTxt=scriptTxt+scriptTxt;
        # scriptTxt=scriptTxt+scriptTxt;
        # scriptTxt=scriptTxt+scriptTxt;
        # scriptTxt=scriptTxt+scriptTxt;
        # scriptTxt=scriptTxt+scriptTxt;
        #scriptTxt=scriptTxt+scriptTxt;
        #scriptTxt=scriptTxt+scriptTxt;
        #scriptTxt=scriptTxt+scriptTxt;
        #scriptTxt=scriptTxt+scriptTxt;
        #scriptTxt=scriptTxt+scriptTxt;
        #scriptTxt=scriptTxt+scriptTxt;
        scriptTxt=translateScript(scriptTxt)
        #print("scriptTxt="+scriptTxt)
        expresiones=scriptTxt.split("\n")
        
        expresiones=wrapScript(expresiones)

        enviar=""

        for expresion in expresiones:
            enviar=enviar+expresion+"\n"
        expresiones=enviar
        #print(expresiones)
        print('waiting for a connection')
        connection, client_address = sock.accept()
        #connection.settimeout(0.025) #timeout mas bajo mas posiblemente exacto
        connection.settimeout(1)
        print('connection from', client_address)
        cont2=0
        respuesta = ""
        
        print(enviar)
        
        try:
            connection.sendall(str.encode(expresion))
            # Receive the data in small chunks and retransmit it
            aux2=1
            while aux2==1:
                aux=1
                data = connection.recv(1024)
                print('received {!r}'.format(data))
                respuesta = respuesta + data.decode("utf-8") 
                print("Data")
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
            
            connection.close()
            print("Excepcion: ")
            print(e)
            aux=1
        finally:
            # Clean up the connection
            print("Cerrado")
            #connection.close()
            #time.sleep(3)
                
        connection.close()
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
if __name__ == '__main__':
    app.run(debug=True, port=serverPort)

