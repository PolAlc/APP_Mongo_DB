from flask import Flask, json
from pymongo import MongoClient
from urllib.parse import urlencode

#no es necesario que se escriba settings.py. Puede ser directamente settings. Si el archivo estuviera en otra carpeta distinta a la del programa, por ejemplo config, se pondría import config.settings
import settings

#en environ está toda la información del sistema operativo, desde por ejemplo, número de procesadores, hasta el contenido del archivo .env
from os import environ

# si imprimo como print(environ), tengo acceso a toda la información del entorno. Esa información está definida como diccionario, entonces si quiero por ejemplo el contenido de la variable DB_USER, se puede escribir como print(environ["DB_USER"]) y se verá el valor
# una buena práctica es no hacer un uso muy directo de la variable, se suele reasignar las variables en constantes, haciendo una réplica de los datos. Esto ayuda a la utilización de estos parámetros en el código
    
USER = environ["DB_USER"]
PASS = environ["DB_PASS"]
HOST = environ["DB_HOST"]
BASE = environ["DB_NAME"]


#La supervariable __name__ tomará por nombre al nombre del archivo py
app = Flask(__name__)

### Mongodb ###
##Estos datos están en parte de conexión de Mongodb, igualmente luego fueron editados. Esta fue la forma inicial de como se configuró la conección, usando query string (o url encode) - parametro1 = valor1 & parametro2 = valor2, etc:
'''
client = MongoClient("mongodb+srv://usuario:password@host/baseDeDatos?retryWrites=true&w=majority&ssl=true&ssl_cert_reqs=CERT_NONE")
'''
#Luego las reglas de conexión en lugar de definirlas con un query string, definió un diccionario
config = {
'retryWrites' : "true",
'w' : "majority",
'ssl' : "true",
'ssl_cert_reqs' : "CERT_NONE"
}

client = MongoClient("mongodb+srv://" + USER + ":" + PASS + "@" + HOST + "/" + BASE + "?" + urlencode(config))

###############

###############
#Flask permite crear rutas y qué ocurre cuando se accede a esas rutas. En esta primera, se está indicando qué hacer cuando accede a la raíz de la ruta ("/"):
@app.route("/")
#Luego qué ocurre al acceder a esa ruta, se define con una función
def home():
    return("Hola mundo desde la home de Flask :D")
###############

###############
#Se agrega otra ruta, que de acceder a ella, traerá estos 5 datos que están harcodeados en formato json (no pasa por la BBDD de mongodb):
@app.route("/users")
def usersTwitter():
    users = [
        { "name" : "smessina_"},
        { "name" : "eanttech" },
        { "name" : "TinchoLutter"},
        { "name" : "bitcoinarg"},
        { "name" : "sasarasa"}
    ]
#Con esta variable "response", se convierte al contenido de la variable users en una respuesta compatible a formato web y en particular con formato json.
#response: Es el contenido. En el ejemplo se usa la función importada json, que convierte users en el formato necesario
#status: es el código de la operación (200 significa si se accede bien)
#mimetype: indica qué tipo de contenido se debe interpretar lo que estamos respondiendo

    response = app.response_class(response = json.dumps(users), status = 200, mimetype = "application/json")

    return response
###############

###############
#En esta otra ruta, toma los 4 nombres de usuario que están cargados en MongoDB y solamente los muestra en la consola:

@app.route("/tweets1")
def getTweets1():
    twitter = client['API-Twitter']['Tweets']
 
    names = twitter.find()
    for name in names:
        print('------')
        print(name)        
        print('------')
    return "Mira la consola..."
###############

###############
#En esta otra ruta, muestra la respuesta de los 4 usuarios cargados en MongoDB, en el navegador. En esta app, también está renombrando la propiedad "name" a "usuario":
    
@app.route("/tweets")
def getTweets():
    twitter = client['API-Twitter']['Tweets']
    names = twitter.find()
    
    result = []

    for name in names:
        item = {
            'usuario' : name['name']
        }
        result.append(item)
    
    return app.response_class(response = json.dumps(result), status = 200, mimetype = "application/json")
##############

##############
#Se configura un parámetro dinámico a la ruta, con una parte fija y una dinámica.
#Lo que se escribe entre "<>", se toma como una variable. Puede llamarse de cualquier forma, en este caso, se nombró como "path". Notar que esa variable se asigna a la función getTweetsDinam():
@app.route("/tweets/<path>")
def getTweetsDinam(path):
    twitter = client['API-Twitter']['Tweets']
        
    if path not in ['people', 'company']:
        result = {'error' : 'Categoria inexistente'}
    else:
        names = twitter.find({'type':path})
    
        result = []

        for name in names:
            item = {
                'usuario' : name['name']
                }
            result.append(item)
    
    return app.response_class(response = json.dumps(result), status = 200, mimetype = "application/json")



#Se configura con qué puerto se conectará al servidor web de flask (en este caso se usó el 3000 al azar - generalmente está libre):
#app.run( port = 3000 )

#Al agregar host = "0.0.0.0", estoy habilitando el uso del router. Esto ya lo habilita a ser usado en una intranet de mi casa. Cuando se corre con esta opción, muestra: http://miip:3000/, que es el ip de mi conexión a internet, con lo cual si ejecuto esto en el navegador de mi teléfono, si éste está en la misma red, se conecta.
app.run( port = 3000, host = "0.0.0.0" )