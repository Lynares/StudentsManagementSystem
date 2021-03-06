# -*- coding: utf-8 -*-

"""

Hello World API implemented using Google Cloud Endpoints.

Defined here are the ProtoRPC messages needed to define Schemas for methods
as well as those methods defined in an API.

Para ver el servidor de exploración:

    https://your_app_id.appspot.com/_ah/api/explorer


 > Estandar de log por terminal <

 Intentamos que el código tenga la mayor depuración posible por terminal ya que son tantos pasos de mensajes
 que es más fácil de detectar errores así. Existe una variable v=1 (por defecto) que habilita todos los mensajes y se sigue
 un estandar más o menos regular.

 Cuando se realiza la llamada a un método de la api se añade justo a la entrada el bloque (ajustado al método):

     #Info de seguimiento
     if v:
         print nombreMicroservicio
         print ' Petición GET a profesores.getProfesor'
         print ' Request: \n '+str(request)+'\n'

 y para conocer la salida otro que siga el formato:

     #Info de seguimiento
     if v:
         print nombreMicroservicio
         print ' Return: '+str(profesor)+'\n'

 para saber a que método se ha llamado y con qué parámetros.

"""


import endpoints
#https://cloud.google.com/appengine/docs/python/tools/protorpc/messages/messageclass
from protorpc import messages
from protorpc import message_types
from protorpc import remote
import os

#Doc de urlfetch: https://cloud.google.com/appengine/docs/python/refdocs/google.appengine.api.urlfetch
#Librerías usadas para la llamada a las APIRest de los microservicios
from google.appengine.api import urlfetch
import urllib

#Para el descubrimiento de los módulos
import urllib2
from google.appengine.api import modules
#Para la decodificaciónd e los datos recibidos en JSON desde las APIs
import jsonpickle

import json

from manejadorImagenes import ManejadorImagenes

#Variable habilitadora del modo verbose
v=True

nombreMicroservicio = '\n ## API Gateway ##'

#Variable del nombre del microservicio de base de datos SBD
sbd="sbd"


# TODO: Replace the following lines with client IDs obtained from the APIs
# Console or Cloud Console.
WEB_CLIENT_ID = 'replace this with your web client application ID'
ANDROID_CLIENT_ID = 'replace this with your Android client ID'
IOS_CLIENT_ID = 'replace this with your iOS client ID'
ANDROID_AUDIENCE = WEB_CLIENT_ID


package = 'Hello'
# Función que recibe una cadena como parámetro y la formatea para resolver el problema de los acentos.
def formatText(cadena):
    return cadena.encode('utf-8').decode('utf-8')

def formatTextInput(cadena):
    return cadena.encode('utf-8')

class MensajeRespuesta(messages.Message):
    message = messages.StringField(1)

#Mensaje que usamos para devolver la información de estado sobre la creación de alguna entidad en el sistema y además devuelve el id en sistema de la identidad creada. (Como por ejemplo en la insercción de un alumno)
class StatusID(messages.Message):
    status = messages.StringField(1)
    statusCode = messages.StringField(2)
    id = messages.IntegerField(3)

class URL(messages.Message):
    url = messages.StringField(1)

class MensajePeticion(messages.Message):
    message = messages.StringField(1)
"""
Como vemos, no aparecen argumentos en el cuerpo de la petición ya que se trata
de una petición de tipo GET.
"""

#######################################
## TIPOS DE MENSAJES QUE MANEJA LA API##
#######################################

"""
A continuación se implementa la estrutura de cada tipo de mensaje que se puede enviar o recibir en
el proyecto en el microservicio de apigateway.
"""

class Alumno(messages.Message):
    nombre = messages.StringField(1)
    apellidos = messages.StringField(2)
    id = messages.StringField(3)

class AlumnoCompleto(messages.Message):
    id = messages.StringField(1)
    nombre = messages.StringField(2)
    apellidos = messages.StringField(3)
    dni = messages.StringField(4)
    direccion = messages.StringField(5)
    localidad = messages.StringField(6)
    provincia = messages.StringField(7)
    fecha_nacimiento = messages.StringField(8)
    telefono = messages.StringField(9)
    imagen = messages.StringField(10)

class ID(messages.Message):
    id = messages.StringField(1)

class ListaAlumnos(messages.Message):
    alumnos = messages.MessageField(Alumno, 1, repeated=True)

class Profesor(messages.Message):
    nombre = messages.StringField(1)
    apellidos = messages.StringField(2)
    id = messages.StringField(3)



class ProfesorCompleto(messages.Message):
    id = messages.StringField(1)
    nombre = messages.StringField(2)
    apellidos = messages.StringField(3)
    dni = messages.StringField(4)
    direccion = messages.StringField(5)
    localidad = messages.StringField(6)
    provincia = messages.StringField(7)
    fecha_nacimiento = messages.StringField(8)
    telefono = messages.StringField(9)

class ListaProfesores(messages.Message):
    profesores = messages.MessageField(Profesor, 1, repeated=True)

class Asignatura(messages.Message):
    id = messages.StringField(1)
    nombre = messages.StringField(2)

class AsignaturaCompleta(messages.Message):
    id = messages.StringField(1)
    nombre = messages.StringField(2)

class ListaAsignaturas(messages.Message):
    asignaturas = messages.MessageField(Asignatura, 1, repeated=True)

class Clase(messages.Message):
    id = messages.StringField(1)
    curso = messages.StringField(2)
    grupo = messages.StringField(3)
    nivel = messages.StringField(4)

#Para ampliar en el futuro y no usar el mismo tipo de mensaje:
class ClaseCompleta(messages.Message):
    id = messages.StringField(1)
    curso = messages.StringField(2)
    grupo = messages.StringField(3)
    nivel = messages.StringField(4)

class ListaClases(messages.Message):
    clases = messages.MessageField(Clase, 1, repeated=True)

class Matricula(messages.Message):
    id_matricula = messages.StringField(1)
    id_alumno = messages.StringField(2)
    id_asociacion = messages.StringField(3)

class ListaMatriculas(messages.Message):
    matriculas = messages.MessageField(Matricula, 1, repeated=True)

class Imparte(messages.Message):
    id_imparte = messages.StringField(1)
    id_profesor = messages.StringField(2)
    id_asociacion = messages.StringField(3)

class ListaImpartes(messages.Message):
    impartes = messages.MessageField(Imparte, 1, repeated=True)

class Asociacion(messages.Message):
    id_asociacion = messages.StringField(1)
    id_clase = messages.StringField(2)
    id_asignatura = messages.StringField(3)
    nombreAsignatura = messages.StringField(4)
    nombreClase = messages.StringField(5)

class ListaAsociaciones(messages.Message):
    asociaciones = messages.MessageField(Asociacion, 1, repeated=True)

#Un nuevo tipo de mensaje para el profesor simple que añade un poco de información necesaria
class ProfesorSimpleExtendido(messages.Message):
    nombre = messages.StringField(1)
    apellidos = messages.StringField(2)
    id = messages.StringField(3)
    idImparte = messages.StringField(4)

class AlumnoSimpleExtendido(messages.Message):
    nombre = messages.StringField(1)
    apellidos = messages.StringField(2)
    id = messages.StringField(3)
    idMatricula = messages.StringField(4)

#####################################################
## Mensajes del servicio de Control de Estudiantes ##
#####################################################
"""
Estructura de mensajes intercambiados en el servicio de Control de estudiantes (sce)
"""

class ControlAsistencia(messages.Message): #Debería llamarse mControlAsistencia (micro)
    asistencia = messages.IntegerField(1, required=True)
    #Si el retraso es 0: no hay retraso 10: retraso de 10 min 20: retraso de 20 min o más
    retraso = messages.IntegerField(2, required=True)
    retrasoJustificado = messages.IntegerField(3, required=True)
    uniforme =  messages.IntegerField(4, required=True)
    id = messages.IntegerField(5, required=True)
    #Campo solo necesario para los controles de asistencia de salida, proceso: obtenerControlAsistencia
    nombreAlumno = messages.StringField(6)

class ListaControlAsistencia(messages.Message):  #Debería llamarse ControlAsistencia
    controles = messages.MessageField(ControlAsistencia, 1, repeated=True)
    idProfesor = messages.IntegerField(2, required=True)
    idClase = messages.IntegerField(3, required=True)
    idAsignatura = messages.IntegerField(4, required=True)
    """
    Campos solo necesarios para los controles de asistencia de salida, proceso:
    """
    nombreClase = messages.StringField(5)
    nombreAsignatura = messages.StringField(6)
    nombreProfesor = messages.StringField(7)
    fecha = messages.StringField(8)

class ResumenControlAsistencia(messages.Message):
    key = messages.IntegerField(1, required=True)
    fecha = messages.StringField(2)
    idClase = messages.IntegerField(3)
    nombreClase = messages.StringField(4)
    idAsignatura = messages.IntegerField(5)
    nombreAsignatura = messages.StringField(6)
    idProfesor = messages.IntegerField(7)
    nombreProfesor = messages.StringField(8)

class ListaResumenControlAsistencia(messages.Message):
    resumenes = messages.MessageField(ResumenControlAsistencia, 1, repeated=True)

#Cuando pedimos los resumenes de los controles de asistencia los podemos pedir usando parámetros o sin ellos.
class ParametrosPeticionResumen(messages.Message):
    idProfesor = messages.IntegerField(1)
    idAsignatura = messages.IntegerField(2)
    idClase = messages.IntegerField(3)
    fechaHora = messages.StringField(4)

#### FIN DE LOS MENSAJES PARA EL SCE


#Definimos un tipo especial de mensaje
class AsociacionCompleta(messages.Message):
    nombreAsignatura = messages.StringField(1)
    listaProfesores = messages.MessageField(ProfesorSimpleExtendido, 2, repeated=True)
    listaAlumnos = messages.MessageField(AlumnoSimpleExtendido, 3, repeated=True)
    idAsociacion = messages.StringField(4)

class salidaLogin(messages.Message):
    idUser = messages.StringField(1, required=True)
    nombre = messages.StringField(2, required=True)
    rol = messages.StringField(3, required=True)




#Decorador que establace nombre y versión de la api
@endpoints.api(name='helloworld', version='v1')
class HelloWorldApi(remote.Service):
    """Helloworld API v1."""


    @endpoints.method(message_types.VoidMessage, MensajeRespuesta, path='holaMundo', http_method='GET', name='holaMundo')
    def getSaludoHolaMundo(self, request):
        '''
        Función de prueba de exposición.
        curl -X GET localhost:8001/_ah/api/helloworld/v1/holaMundo
        '''
        return MensajeRespuesta(message='Hola mundo! \n')




    ##############################################
    ##   métodos de ALUMNOS                       #
    ##############################################

    @endpoints.method(message_types.VoidMessage, ListaAlumnos,
                      #path=nombre del recurso a llamar
                      path='alumnos/getAlumnos', http_method='GET',
                      #Puede que sea la forma en la que se llama desde la api:
                      #response = service.alumnos().listGreeting().execute()
                      name='alumnos.getAlumnos')

    def getAlumnos(self, unused_request):
        """
        getAlumnos()   [GET sin parámetros]

        Devuelve una lista con todos los estudiantes registrados en el sistema, de forma simplificada (solo nombre y ID)

        Llamada desde terminal:
        curl -X GET localhost:8001/_ah/api/helloworld/v1/alumnos/getAlumnos
        Llamada desde JavaScript:
        response =service.alumnos().getAlumnos().execute()
        """
        #Transformación de la llamada al endpoints a la llamada a la api rest del servicio.

        #Info de seguimiento
        if v:
            print nombreMicroservicio
            print "Petición GET a alumnos.getAlumnos"
            print '\n'

        #Conexión a un microservicio específico:

        module = modules.get_current_module_name()
        instance = modules.get_current_instance_id()

        #Le decimos a que microservicio queremos conectarnos (solo usando el nombre del mismo), GAE descubre su URL solo.
        url = "http://%s/" % modules.get_hostname(module=sbd)
        #Añadimos el recurso al que queremos conectarnos.
        url+="alumnos"
        #result = urllib2.urlopen(url)
        #print result

        if v:
            print "Llamando a: "+str(url)
        #Llamamos al microservicio y recibimos los resultados con URLFetch
        #Al no especificar nada se llama al método GET de la URL.
        result = urlfetch.fetch(url)

        #Vamos a intentar consumir los datos en JSON y convertirlos a un mensje enviable :)

        if v:
            print nombreMicroservicio
            print "Resultados de la petición: "
            print result.content
            print "Código de estado: "+str(result.status_code)+'\n'

        listaAlumnos = jsonpickle.decode(result.content)

        """
        miListaAlumnos=ListaAlumnos()
        miListaAlumnos.alumnos = listaAlumnos
        """

        #Creamos un vector
        alumnosItems= []
        #Que rellenamos con todo los alumnos de la listaAlumnos

        if v:
            print "Construcción del mensaje de salida: \n"

        for alumno in listaAlumnos:
            idAlumno = str(alumno.get('id'))
            nombreAlumno = alumno.get('nombre')
            apellidosAlumno = alumno.get('apellidos')

            alumnosItems.append(Alumno( id=idAlumno, nombre=formatText(nombreAlumno), apellidos=formatText(apellidosAlumno) ) )


        return ListaAlumnos(alumnos=alumnosItems)

    @endpoints.method(ID, AlumnoCompleto, path='alumnos/getAlumno', http_method='GET', name='alumnos.getAlumno')
    def getAlumno(self,request):
        """
        getAlumno() [GET con dni]

        Devuelve toda la información de un estudiante en caso de estar en el sistema.

        Llamada ejemplo desde terminal:
        curl -X GET localhost:8001/_ah/api/helloworld/v1/alumnos/getAlumno?id=2
        """

        #Info de seguimiento
        if v:
            print nombreMicroservicio
            print "Petición GET a alumnos.getAlumno"
            print "request: "+str(request)
            print '\n'

        #Cuando se llama a este recurso lo que se quiere es recibir toda la información
        #de una entidad Alumno, para ello primero vamos a recuperar la información del microsrevicio apropiado:

        #Conexión a un microservicio específico:
        module = modules.get_current_module_name()
        instance = modules.get_current_instance_id()

        #Le decimos al microservicio que queremos conectarnos (solo usando el nombre del mismo), GAE descubre su URL solo.
        url = "http://%s/" % modules.get_hostname(module=sbd)

        """
        Según la doc. de urlfetch (ver arriba) no podemos pasar parámetros con el payload, así que como conocemos
        la api del microservicios al que vamos a llamr realizamos la petición bajo su especificacion, según la cual
        solo tenemos que llamar a /alumnos/<id_alumno> entonces concatenamos a la url esa id qu recibimos en la llamada
        a este procedimiento.
        """
        #Recursos más entidad
        url+='alumnos/'+request.id

        if v:
            print "Llamando a: "+str(url)

        #Petición al microservicio
        result = urlfetch.fetch(url=url, method=urlfetch.GET)

        print "RESULTADO:"+str(result.status_code)
        #print result.content
        if v:
            print result.status_code
        if str(result.status_code) == '400':
            raise endpoints.BadRequestException('Peticion erronea')

        if str(result.status_code) == '404':
            raise endpoints.NotFoundException('Alumno con ID %s no encontrado.' % (request.dni))

        alumno = jsonpickle.decode(result.content)

        #Infro después de la petición:
        if v:
            print nombreMicroservicio
            print "Resultado de la petición: "
            print result.content
            print "\nCódigo de estado: "+str(result.status_code)+'\n'




        #Componemos un mensaje de tipo AlumnoCompleto.
        #Las partes que son enteros las pasamos a string para enviarlos como mensajes de tipo string.

        #Ojo, solo los elementos que no sean null se enviarán. Cuando un alumno no tenga imagen y pr tanto su valor
        #en la base de datos sea null no se recibirá el campo imagen en el JSON que la API G devuelve.

        alumno = AlumnoCompleto(id=str(alumno.get('id')),
                                nombre=formatText(alumno.get('nombre')),
                                apellidos=formatText(alumno.get('apellidos')),
                                dni=str(alumno.get('dni')),
                                direccion=formatText(alumno.get('direccion')),
                                localidad=formatText(alumno.get('localidad')),
                                provincia=formatText(alumno.get('provincia')),
                                fecha_nacimiento=str(alumno.get('fecha_nacimiento')),
                                telefono=alumno.get('telefono'),
                                imagen=alumno.get('urlImagen')
                                )

        return alumno

    class AlumnoCompletoConImagen(messages.Message):
        id = messages.StringField(1)
        nombre = messages.StringField(2)
        apellidos = messages.StringField(3)
        dni = messages.StringField(4)
        direccion = messages.StringField(5)
        localidad = messages.StringField(6)
        provincia = messages.StringField(7)
        fecha_nacimiento = messages.StringField(8)
        telefono = messages.StringField(9)
        #En esta ocasión la imagen no es una URL sino los Bytes en crudo.
        imagen  = messages.BytesField(10)

    @endpoints.method(AlumnoCompletoConImagen, StatusID, path='alumnos/insertarAlumno2', http_method='POST', name='alumnos.insertarAlumno2')
    def insertar_alumno2(self, request):
        """

        Función que inserta un alumno en el sistema con o sin imagen.

        Ejemplo de llamada SIN imagen:
        curl -i -d "nombre=Juan&apellidos=Fernandez&dni=45301218&direccion=Calle&localidad=Jerezfrontera&provincia=Granada&fecha_nacimiento=1988-2-6&telefono=699164459" -X POST -G localhost:8001/_ah/api/helloworld/v1/alumnos/insertarAlumno2

        Ejmplo de llamada CON imagen:

        curl -d "nombre=Juan&apellidos=Fernandez&dni=45301218&direccion=Calle&localidad=Jerezfrontera&provincia=Granada&fecha_nacimiento=1988-2-6&telefono=699164459" --data-urlencode 'imagen='"$( base64 profile.jpg)"''  -X POST -G localhost:8001/_ah/api/helloworld/v1/alumnos/insertarAlumno2
        """

        if v:
            print nombreMicroservicio
            print "Petición POST a alumnos.insertarAlumno2"
            print "Contenido de la petición:"
            print request
            print '\n'

        #Construimos un diccionario con los datos del alumno recibidos en la petición.
        datos = {
          "nombre": formatTextInput(request.nombre),
          "apellidos": formatTextInput(request.apellidos),
          "dni": request.dni,
          "direccion": formatTextInput(request.direccion),
          "localidad": formatTextInput(request.localidad),
          "provincia": formatTextInput(request.provincia),
          "fecha_nacimiento": request.fecha_nacimiento,
          "telefono": request.telefono
        }

        #Sea con imagen o sin imagen insertamos al alumno en el sistema:
        #Conformamos la dirección:
        url = "http://%s/" % modules.get_hostname(module=sbd)
        #Añadimos el servicio al que queremos conectarnos.
        url+="alumnos"

        #Codificamos los datos.
        form_data = urllib.urlencode(datos)
        #Realizamos la petición al servicio con los datos codificados al microservicio apropiado.
        result = urlfetch.fetch(url=url, payload=form_data, method=urlfetch.POST)
        if v:
            print nombreMicroservicio
            print "Resultado de la petición: "
            print result.content
            print "Código de estado: "
            print result.status_code
            print '\n\n'

        #Analizamos la respuesta y si todo ha ido bien habremos recibido algo así: {'idAlumno': '42', 'status': 'OK'}
        json = jsonpickle.decode(result.content)

        #Definimos el mensaje de salida:
        salida = ''

        if json['status'] == 'OK':
            #Es que el alumno se ha guardado con éxito, entonces procedemos a guardar su imagen

            #Si se detecta que no se ha enviado información en el campo imagen, es que no se está enviando una imagen:
            if request.imagen == None:
                print 'Petición a insertarAlumno2 SIN imagen en el request.\n'
                salida = json['status']

            else:
                print 'Petición a insertarAlumno2 CON imagen en el request.\n'

                #Pero antes ponemos el nombre de forma correcta, usando el id del alumno y la extensión de la imagen
                nombreImagen = 'alumnos/imagenes_perfil/' + json['idAlumno'] + '.jpg'

                urlImagenAlumno = ManejadorImagenes.CreateFile(nombreImagen, request.imagen)

                #Una vez guardada la imagen pasamos a setear el campo imagen del alumno en cuestión.
                url2 = "http://%s/" % modules.get_hostname(module=sbd)
                url2+="alumnos/"+json['idAlumno']

                #Añadimos la imagen a los datos:
                datos['imagen'] = urlImagenAlumno;

                resultadoModificacion = urlfetch.fetch(url=url2, payload=urllib.urlencode(datos), method=urlfetch.POST)

                print 'Resultado Modificacion'
                print str(resultadoModificacion.content)
                salida = resultadoModificacion.content
                #json2 = jsonpickle.decode(resultadoModificacion.content)
                #salida = json2['status']

        return StatusID(status=salida, id=int(json['idAlumno']))


    #### possibly deprecated ####
    @endpoints.method(AlumnoCompleto,MensajeRespuesta, path='alumnos/insertarAlumno', http_method='POST', name='alumnos.insertarAlumno')
    def insertar_alumno(self, request):
        '''
        insertarAlumno()  [POST con todos los atributos de un alumno]

        Introduce un nuevo alumno en el sistema.

        Ejemplo de llamada en terminal:
        curl -i -d "nombre=Juan&dni=45301218Z&direccion=Calle&localidad=Jerezfrontera&provincia=Granada&fecha_nacimiento=1988-2-6&telefono=699164459" -X POST -G localhost:8001/_ah/api/helloworld/v1/alumnos/insertarAlumno
        (-i para ver las cabeceras)

        '''

        if v:
            print nombreMicroservicio
            print "Petición POST a alumnos.insertarAlumno"
            print "Contenido de la petición:"
            print str(request)
            print '\n'

        #Si no tenemos todos los atributos entonces enviamos un error de bad request.
        if request.nombre==None or request.apellidos==None or request.dni==None or request.direccion==None or request.localidad==None or request.provincia==None or request.fecha_nacimiento==None or request.telefono==None:
            raise endpoints.BadRequestException('Peticion erronea, faltan datos.')

        #Conformamos la dirección:
        url = "http://%s/" % modules.get_hostname(module=sbd)
        #Añadimos el servicio al que queremos conectarnos.
        url+="alumnos"

        #Extraemos lo datos de la petición al endpoints
        form_fields = {
          "nombre": formatTextInput(request.nombre),
          "apellidos": formatTextInput(request.apellidos),
          "dni": request.dni,
          "direccion": formatTextInput(request.direccion),
          "localidad": formatTextInput(request.localidad),
          "provincia": formatTextInput(request.provincia),
          "fecha_nacimiento": request.fecha_nacimiento,
          "telefono": request.telefono
        }

        if request.imagen != None:
            print 'Hay imagen recibida en insertarAlumno()'
            form_fields['imagen'] = request.imagen
            print form_fields


        if v:
            print "Llamando a: "+url
            print 'DATOS'
            print form_fields


        #Doc de urlfetch: https://cloud.google.com/appengine/docs/python/refdocs/google.appengine.api.urlfetch
        form_data = urllib.urlencode(form_fields)
        #Realizamos la petición al servicio con los datos pasados al endpoint
        result = urlfetch.fetch(url=url, payload=form_data, method=urlfetch.POST)


        #Infro después de la petición:
        if v:
            print nombreMicroservicio
            print "Resultado de la petición: "
            print result.content
            print "Código de estado: "
            print result.status_code

        if str(result.status_code) == '404':
            raise endpoints.NotFoundException('Alumno con ID %s ya existe en el sistema.' % (request.dni))

        #return MensajeRespuesta(message="Todo OK man!")
        #Mandamos la respuesta que nos devuelve la llamada al microservicio:
        return MensajeRespuesta(message=result.content)

    @endpoints.method(ID,MensajeRespuesta,path='alumnos/delAlumno', http_method='DELETE', name='alumnos.delAlumno')
    def eliminar_alumno(self, request):

        '''
        #Ejemplo de borrado de un recurso pasando el dni de un alumno
        curl -d "id=87" -X DELETE -G localhost:8001/_ah/api/helloworld/v1/alumnos/delAlumno
        '''

        if v:
            print nombreMicroservicio
            print "Petición DELETE a alumnos.delAlumno"
            print "Contenido de la petición:"
            print str(request)
            print '\n'

        #Conformamos la dirección:
        url = "http://%s/" % modules.get_hostname(module=sbd)

        '''
        Parece que urlfetch da problemas a al hora de pasar parámetros (payload) cuando se trata del
        método DELETE.
        Extracto de la doc:
        payload: POST, PUT, or PATCH payload (implies method is not GET, HEAD, or DELETE). this is ignored if the method is not POST, PUT, or PATCH.
        Además no somos los primeros en encontrarse este problema:
        http://grokbase.com/t/gg/google-appengine/13bvr5qjyq/is-there-any-reason-that-urlfetch-delete-method-does-not-support-a-payload

        Por eso en lugar de pasar los datos por payload los añadimos a la url, que es algo equivalente.

        '''
        #Extraemos el argumento id de la petición y la añadimos a la URL
        url+='alumnos/'+request.id

        #1. Primero consultamos si ese alumno tenía imagen (porque tendremos que borrarla del Cloud Storage)
        datosAlumno = urlfetch.fetch(url=url, method=urlfetch.GET)
        jsonDatosAlumno = jsonpickle.decode(datosAlumno.content)

        #2. Si se tiene imagen se manda a borrar
        if(jsonDatosAlumno['urlImagen']!='NULL'):

            print '\n Modificando imagen actual del usuario con id: '+str(jsonDatosAlumno['id'])

            #1. Se ha de borrar la antigua imagen del Cloud Storage
            #Primero componenmos el nombre de aso aimagen:
            nombreImagen = 'alumnos/imagenes_perfil/' + str(jsonDatosAlumno['id']) + '.jpg'
            #Después se manda a borrar
            print 'Eliminacion imagen:' + str(ManejadorImagenes.DeleteFile2(nombreImagen))


        #3. Realizamos la petición a la url del servicio con el método apropiado para borrarlos definitivament.
        result = urlfetch.fetch(url=url, method=urlfetch.DELETE)

        #Infro después de la petición:
        if v:
            print nombreMicroservicio
            print "Resultado de la petición: "
            print result.content
            print "Código de estado: "
            print result.status_code


        #Mandamos la respuesta que nos devuelve la llamada al microservicio:
        return MensajeRespuesta(message=result.content)

    @endpoints.method(AlumnoCompletoConImagen,MensajeRespuesta,path='alumnos/modAlumnoCompleto2', http_method='POST', name='alumnos.modAlumnoCompleto2')
    def modificarAlumnoCompleto2(self, request):
        '''
        Ejemplo de llamada SIN imagen:
        curl -i -d "id=85&nombre=Maria2&apellidos=Fernandez&dni=45301218&direccion=Calle&localidad=Jerezfrontera&provincia=Granada&fecha_nacimiento=1988-2-6&telefono=699164459" -X POST -G localhost:8001/_ah/api/helloworld/v1/alumnos/modAlumnoCompleto2

        Ejmplo de llamada CON imagen:

        curl -i -d "id=87&nombre=Juan&apellidos=Fernandez&dni=45301218&direccion=Calle&localidad=Jerezfrontera&provincia=Granada&fecha_nacimiento=1988-2-6&telefono=699164459" --data-urlencode 'imagen='"$( base64 profile.jpg)"''  -X POST -G localhost:8001/_ah/api/helloworld/v1/alumnos/modAlumnoCompleto2

        Con otra imagen:
        curl -i -d "id=87&nombre=Juan&apellidos=Fernandez&dni=45301218&direccion=Calle&localidad=Jerezfrontera&provincia=Granada&fecha_nacimiento=1988-2-6&telefono=699164459" --data-urlencode 'imagen='"$( base64 profile2.jpg)"''  -X POST -G localhost:8001/_ah/api/helloworld/v1/alumnos/modAlumnoCompleto2

        Ejemplo de llamada con ELIMINACION de imagen:
        curl -i -d "imagen=ZGVs&id=87&nombre=Juan&apellidos=Fernandez&dni=45301218&direccion=Calle&localidad=Jerezfrontera&provincia=Granada&fecha_nacimiento=1988-2-6&telefono=699164459"   -X POST -G localhost:8001/_ah/api/helloworld/v1/alumnos/modAlumnoCompleto2


        Ojo!
        En el caso de que traiga una imagen debe comprobar que es distinta (la url) a la que el usuario ya disponía y en caso de serlo mandar
        a borrar la antigua imagen con el manejador de imágenes y solo cuando se haya grabado correctamente en la base de datos el usuario
        y eliminada correctamente la foto del datastore enviar el ok.


        '''

        if v:
            print nombreMicroservicio
            print "Petición POST a alumnos.modAlumnoCompleto2"
            print "Contenido de la petición:"
            #print str(request)
            print '\n'



        url = "http://%s/" % modules.get_hostname(module=sbd)

        #Añadimos el recurso al que queremos conectarnos, colección alumnos / alumno con id concreto.
        url+="alumnos/"+request.id

        #Extraemos lo datos de la petición que se reciben aquí en el endpoints
        datos = {
          "nombre": formatTextInput(request.nombre),
          "apellidos": formatTextInput(request.apellidos),
          "dni": formatTextInput(request.dni),
          "direccion": formatTextInput(request.direccion),
          "localidad": formatTextInput(request.localidad),
          "provincia": formatTextInput(request.provincia),
          "fecha_nacimiento": request.fecha_nacimiento,
          "telefono": request.telefono
        }


        # La imagen se quiere sustituir #
        if request.imagen is not None:
            print '\n\nHAY imagen, la imagen actual se quiere actualizar. \n\n'
            #1. Averiguamos si el usuario tenía imagen ya o no, para borrarla, usamos la url especificada antes pero con el metodo GET
            datosAlumno = urlfetch.fetch(url=url, method=urlfetch.GET)
            jsonDatosAlumno = jsonpickle.decode(datosAlumno.content)

            print jsonDatosAlumno

            #### Si el usuario no tenía imagen: ####
            if(jsonDatosAlumno['urlImagen']=='NULL'):

                print 'Grabando imagen al usuario con id: '+str(jsonDatosAlumno['id'])

                #1. Se graba la imagen en el Cloud Storage
                nombreImagen = 'alumnos/imagenes_perfil/' + str(jsonDatosAlumno['id']) + '.jpg'

                urlImagenAlumno = ManejadorImagenes.CreateFile(nombreImagen, request.imagen)

                #2. Y después se modifican los datos del alumno, añadiendo la url a esta

                #Una vez guardada la imagen pasamos a setear el campo imagen del alumno en cuestión.
                url2 = "http://%s/" % modules.get_hostname(module=sbd)
                url2+="alumnos/"+str(jsonDatosAlumno['id'])

                #Añadimos la imagen a los datos:
                datos['imagen'] = urlImagenAlumno;
                #Realizamos la modificaion llamando a la api del microservicio.
                resultadoModificacion = urlfetch.fetch(url=url2, payload=urllib.urlencode(datos), method=urlfetch.POST)

                print 'Resultado Modificacion'
                print str(resultadoModificacion.content)

            #### Si el usuario SI tenía imagen ####
            if(jsonDatosAlumno['urlImagen']!='NULL'):

                print '\n Modificando imagen actual del usuario con id: '+str(jsonDatosAlumno['id'])

                #1. Se ha de borrar la antigua imagen del Cloud Storage
                #Primero componenmos el nombre de l aimagen:
                nombreImagen = 'alumnos/imagenes_perfil/' + str(jsonDatosAlumno['id']) + '.jpg'
                #Después se manda a borrar
                print 'Eliminacion imagen:' + str(ManejadorImagenes.DeleteFile2(nombreImagen))


                #2. Se debe de guardar la nueva, con el mismo nombre:
                urlImagenAlumno = ManejadorImagenes.CreateFile(nombreImagen, request.imagen)


                #3. Se ha de modificar la url en los datos del estudiante
                #Una vez guardada la imagen pasamos a setear el campo imagen del alumno en cuestión.
                url2 = "http://%s/" % modules.get_hostname(module=sbd)
                url2+="alumnos/"+str(jsonDatosAlumno['id'])

                #Añadimos la imagen a los datos:
                datos['imagen'] = urlImagenAlumno;
                #Realizamos la modificaion llamando a la api del microservicio.
                resultadoModificacion = urlfetch.fetch(url=url2, payload=urllib.urlencode(datos), method=urlfetch.POST)

                print 'Resultado Modificacion'
                print str(resultadoModificacion.content)


        # NO HAY IMAGEN #
        if not request.imagen:
            print '\n\n No hay imagen \n\n'
            #En el caso de que no haya imagen en la petición es que se quiere mantener la que está y solo modificar los datos.
            result = urlfetch.fetch(url=url, payload=urllib.urlencode(datos), method=urlfetch.POST)
            print 'Respuesta'
            print result.content

        print request.imagen;

        # NO HAY IMAGEN y además se quiere eliminar la que el usuario tenga #
        if  request.imagen == 'del':
            print '\n\n El parámetro pasado es ZGVs (del en Base64), la imagen actual se quiere borrar. \n\n'
            #1. Borrar la imagen del Cloud Storage
            salida = ManejadorImagenes.DeleteFile2(nombreImagen = 'alumnos/imagenes_perfil/' + request.id + '.jpg')
            print salida;
            #2. Borrar la url que de la imagen tiene el user en sus datos. (modificar al alumno)
            datos['imagen'] = 'NULL';
            result = urlfetch.fetch(url=url, payload=urllib.urlencode(datos), method=urlfetch.POST)
            print 'Respuesta'
            print result.content



        return MensajeRespuesta(message='OK')

    #### possibly deprecated ####
    @endpoints.method(AlumnoCompleto,MensajeRespuesta,path='alumnos/modAlumnoCompleto', http_method='POST', name='alumnos.modAlumnoCompleto')
    def modificarAlumnoCompleto(self, request):
        '''

        modificarAlumnoCompleto()  [POST]

        Modifica todos los atributos de un alumno, aunque algunos queden igual.

        curl -d "id=1&nombre=Pedro&apellidos=Torrssr&dni=23&direccion=CREalCartuja&localidad=Granada&provincia=Granada&fecha_nacimiento=1988-12-4&telefono=23287282" -i -X POST -G localhost:8001/_ah/api/helloworld/v1/alumnos/modAlumnoCompleto
        HTTP/1.1 200 OK
        content-type: application/json
        Cache-Control: no-cache
        Expires: Fri, 01 Jan 1990 00:00:00 GMT
        Server: Development/2.0
        Content-Length: 20
        Server: Development/2.0
        Date: Mon, 14 Mar 2016 10:17:12 GMT

        {
         "message": "OK"
        }


        Ojo!
        En el caso de que traiga una imagen debe comprobar que es distinta (la url) a la que el usuario ya disponía y en caso de serlo mandar
        a borrar la antigua imagen con el manejador de imágenes y solo cuando se haya grabado correctamente en la base de datos el usuario
        y eliminada correctamente la foto del datastore enviar el ok.


        '''

        if v:
            print nombreMicroservicio
            print "Petición POST a alumnos.modAlumnoCompleto"
            print "Contenido de la petición:"
            print str(request)
            print '\n'

        if request.nombre==None or request.apellidos==None or request.dni==None or request.direccion==None or request.localidad==None or request.provincia==None or request.fecha_nacimiento==None or request.telefono==None:
            raise endpoints.BadRequestException('Peticion erronea, faltan datos.')

        url = "http://%s/" % modules.get_hostname(module=sbd)

        #Añadimos el recurso al que queremos conectarnos, colección alumnos / alumno con id concreto.
        url+="alumnos/"+request.id

        #Extraemos lo datos de la petición que se reciben aquí en el endpoints
        form_fields = {
          "nombre": formatTextInput(request.nombre),
          "apellidos": formatTextInput(request.apellidos),
          "dni": formatTextInput(request.dni),
          "direccion": formatTextInput(request.direccion),
          "localidad": formatTextInput(request.localidad),
          "provincia": formatTextInput(request.provincia),
          "fecha_nacimiento": request.fecha_nacimiento,
          "telefono": request.telefono
        }


        print '\n\nComprobación de la imagen recibida, esté o no\n\n'

        if not request.imagen:
            print '\n\n No hay imagen \n\n'

        print request.imagen;

        if request.imagen != None or request.imagen == 'NULL':
            print 'Hay imagen recibida en modAlumno()'
            form_fields['imagen'] = request.imagen
            print form_fields


            '''
            En este momento se está recibiendo una URL en el campo imagen y por tanto tenemos que comprobar si es la misma que el usuario ya tenía.
            Si es la misma, no se hace nada y el proceso sigue igual, pero si es distinta se debe eliminar la anterior para que no se acumule basura en el servidor
            y después el proceso sigue igual.
            '''

            print '\n\n Comprobación de la igualdad de la imagen \n\n'

            #Para eso primero pasamos los datos de la base de datos del estudiante:
            #Lo único que modificamos es el método con el que se lama a la colección alumnos con el id de uno de ellos
            respuesta = urlfetch.fetch(url=url, method=urlfetch.GET)
            print 'respuesta'
            print respuesta.content
            alumno = jsonpickle.decode(respuesta.content)
            #Se comprueba el dato recibido desde la base de datos con el pasado en la petición al endpoint.
            if alumno.get('urlImagen') == request.imagen:
                print '\n Se trata de la misma imagen (NO SE HA CAMBIADO ESTA) no se hace nada \n'
            else:
                if alumno.get('urlImagen')!= 'NULL':
                    print '\n Se trata de imágenes distintas, hay que mandar a borrar la antigua. \n'
                    #Mandamos a borrar la url de la imagen antingua del alumno.
                    ManejadorImagenes.DeleteFile(alumno.get('urlImagen'))
                #Ya que pùede que no tenga imagen antes y no hay que borrar nada.




        if v:
            print "Llamando a: "+url

        form_data = urllib.urlencode(form_fields)
        result = urlfetch.fetch(url=url, payload=form_data, method=urlfetch.POST)


        #Infro después de la petición:
        if v:
            print nombreMicroservicio
            print "Resultado de la petición: "
            print result.content
            print "Código de estado: "
            print result.status_code

        #return MensajeRespuesta(message="Todo OK man!")
        #Mandamos la respuesta que nos devuelve la llamada al microservicio:
        return MensajeRespuesta(message=result.content)

    # Métodos de información sobre relaciones con otras entidades

    @endpoints.method(ID, ListaProfesores, path='alumnos/getProfesoresAlumno', http_method='GET', name='alumnos.getProfesoresAlumno')
    def getProfesoresAlumno(self, request):
        '''
        Devuelve una lista con los datos completos de los profesores que dan clase al alumno de dni pasado
        curl -i -X GET localhost:8001/_ah/api/helloworld/v1/alumnos/getProfesoresAlumno?id=1
        '''
        #Transformación de la llamada al endpoints a la llamada a la api rest del servicio.
        if v:
            print ("Ejecución de getProfesoresAlumno en apigateway")

        #Conexión a un microservicio específico:

        module = modules.get_current_module_name()
        instance = modules.get_current_instance_id()
        #Le decimos a que microservicio queremos conectarnos (solo usando el nombre del mismo), GAE descubre su URL solo.
        url = "http://%s/" % modules.get_hostname(module=sbd)

        #Añadimos a la url la coleccion (alumnos), el recurso (alumno dado por su dni) y el recurso anidado de este (profesores)
        url+='alumnos/'+str(request.id)+"/profesores"


        print url

        #Realizamos la petición
        result = urlfetch.fetch(url)

        #Vamos a intentar consumir los datos en JSON y convertirlos a un mensje enviable :)

        print "IMPRESION DE LOS DATOS RECIBIDOS"
        print result.content
        listaProfesores = jsonpickle.decode(result.content)

        #Creamos un vector
        profesoresItems= []
        #Que rellenamos con todo los alumnos de la listaAlumnos
        for profesor in listaProfesores:
            profesoresItems.append(Profesor( nombre=formatText(profesor.get('nombre')), apellidos=formatText(profesor.get('apellidos')), id=str(profesor.get('id'))))

        #Los adaptamos al tipo de mensaje y enviamos
        #return Greeting(message=str(result.content))
        return ListaProfesores(profesores=profesoresItems)

    @endpoints.method(ID, ListaAsignaturas, path='alumnos/getAsignaturasAlumno', http_method='GET', name='alumnos.getAsignaturasAlumno')
    def getAsignaturasAlumno(self, request):
        '''
        Devuelve una lista con los datos completos de las asignatuas en las que está matriculado el alumno con dni pasado.
        Ejemplo de llamada:
        curl -i -X GET localhost:8001/_ah/api/helloworld/v1/alumnos/getAsignaturasAlumno?id=1
        '''
        if v:
            print ("Ejecución de getAsignaturasAlumno en apigateway")
        module = modules.get_current_module_name()
        instance = modules.get_current_instance_id()
        url = "http://%s/" % modules.get_hostname(module=sbd)
        url+='alumnos/'+request.id+"/asignaturas"
        result = urlfetch.fetch(url)
        if v:
            print result.content
        listaAsignaturas = jsonpickle.decode(result.content)
        print listaAsignaturas
        asignaturasItems= []
        for asignatura in listaAsignaturas:
            asignaturasItems.append( Asignatura( id=str(asignatura.get('id')), nombre=formatText(asignatura.get('nombre')) ) )
        return ListaAsignaturas(asignaturas=asignaturasItems)

    @endpoints.method(ID, ListaClases, path='alumnos/getClasesAlumno', http_method='GET', name='alumnos.getClasesAlumno')
    def getClasesAlumno(self, request):
        '''
        Devuelve una lista con los datos completos de las clases en las que está matriculado el alumno con dni pasado.
        Ejemplo de llamada:
        curl -i -X GET localhost:8001/_ah/api/helloworld/v1/alumnos/getClasesAlumno?id=1
        '''
        if v:
            print ("Ejecución de getCursosAlumno en apigateway")
        module = modules.get_current_module_name()
        instance = modules.get_current_instance_id()
        url = "http://%s/" % modules.get_hostname(module=sbd)
        url+='alumnos/'+request.id+"/clases"
        result = urlfetch.fetch(url)
        if v:
            print result.content
        listaClases = jsonpickle.decode(result.content)
        print listaClases
        clasesItems= []
        for clase in listaClases:
            clasesItems.append(Clase(id=str(clase.get('id')),curso=str(clase.get('curso')),grupo=str(clase.get('grupo')),nivel=str(clase.get('nivel'))))
        return ListaClases(clases=clasesItems)


    ##############################################
    #   métodos de PROFESORES                    #
    ##############################################

    @endpoints.method(message_types.VoidMessage, ListaProfesores, path='profesores/getProfesores', http_method='GET', name='profesores.getProfesores')
    def getProfesores(self, unused_request):
        '''
        Devuelve una lista con todos los profesores registrados en el sistema, de forma simplificada (solo nombre y ID)

        Llamada desde terminal:
        curl -X GET localhost:8001/_ah/api/helloworld/v1/profesores/getProfesores
        Llamada desde JavaScript:
        response =service.profesores.getProfesores().execute()
        '''
        #Identificación del módulo en el que estamos.
        module = modules.get_current_module_name()
        instance = modules.get_current_instance_id()

        #Leclear decimos a que microservicio queremos conectarnos (solo usando el nombre del mismo), GAE descubre su URL solo.
        url = "http://%s/" % modules.get_hostname(module=sbd)
        #Añadimos el recurso al que queremos conectarnos.
        url+="profesores"
        if v:
            print str(url)
        #Al no especificar nada se llama al método GET de la URL.
        result = urlfetch.fetch(url)
        if v:
            print result.content
        listaProfesores = jsonpickle.decode(result.content)

        #Creamos un vector
        profesoresItems= []
        #Que rellenamos con todo los profesores de la listaProfesores
        for profesor in listaProfesores:
            profesoresItems.append(Profesor( nombre=str(profesor.get('nombre')), apellidos=str(profesor.get('apellidos')), id=str(profesor.get('id'))  ))

        #Los adaptamos al tipo de mensaje y enviamos
        #return Greeting(message=str(result.content))
        return ListaProfesores(profesores=profesoresItems)

    @endpoints.method(ID, ProfesorCompleto, path='profesores/getProfesor', http_method='GET', name='profesores.getProfesor')
    def getProfesor(self,request):
        '''
        Devuelve toda la información de un profesor en caso de estar en el sistema.

        Llamada ejemplo desde terminal:
        curl -X GET localhost:8001/_ah/api/helloworld/v1/profesores/getProfesor?id=1
        '''

        #Info de seguimiento
        if v:
            print nombreMicroservicio
            print ' Petición GET a profesores.getProfesor'
            print ' Request: \n '+str(request)+'\n'

        #Cuando se llama a este recurso lo que se quiere es recibir toda la información
        #de una entidad Alumno, para ello primero vamos a recuperar la información del microsrevicio apropiado:

        #Conexión a un microservicio específico:
        module = modules.get_current_module_name()
        instance = modules.get_current_instance_id()

        #Le decimos al microservicio que queremos conectarnos (solo usando el nombre del mismo), GAE descubre su URL solo.
        url = "http://%s/" % modules.get_hostname(module=sbd)

        '''
        Según la doc. de urlfetch (ver arriba) no podemos pasar parámetros con el payload, así que como conocemos
        la api del microservicios al que vamos a llamr realizamos la petición bajo su especificacion, según la cual
        solo tenemos que llamar a /alumnos/<id_alumno> entonces concatenamos a la url esa id qu recibimos en la llamada
        a este procedimiento.
        '''
        #Recursos más entidad
        url+='profesores/'+request.id

        if v:
            print "Llamando a: "+str(url)

        #Petición al microservicio
        result = urlfetch.fetch(url=url, method=urlfetch.GET)

        print "RESULTADO:"+str(result.status_code)
        #print result.content
        if v:
            print result.status_code
        if str(result.status_code) == '400':
            raise endpoints.BadRequestException('Peticion erronea')

        if str(result.status_code) == '404':
            raise endpoints.NotFoundException('Profesor con ID %s no encontrado.' % (request.id))

        profesor = jsonpickle.decode(result.content)

        #Infro después de la petición:
        if v:
            print nombreMicroservicio
            print "Resultado de la petición: "
            print result.content
            print "\nCódigo de estado: "+str(result.status_code)+'\n'


        #Componemos un mensaje de tipo AlumnoCompleto.
        #Las partes que son enteros las pasamos a string para enviarlos como mensajes de tipo string.
        #Los campos que tengan NULL en la bd no se pasan al tipo message y ese campo queda vaćio y no se muestra.
        profesor = ProfesorCompleto(id=str(profesor.get('id')),
                                nombre=profesor.get('nombre'),
                                apellidos=profesor.get('apellidos'),
                                dni=str(profesor.get('dni')),
                                direccion=profesor.get('direccion'),
                                localidad=profesor.get('localidad'),
                                provincia=profesor.get('provincia'),
                                fecha_nacimiento=str(profesor.get('fecha_nacimiento')),
                                telefono=str(profesor.get('telefono'))
                                )

        #Info de seguimiento
        if v:
            print nombreMicroservicio
            print ' Return: '+str(profesor)+'\n'

        return profesor

    @endpoints.method(ProfesorCompleto, StatusID, path='profesores/insertarProfesor', http_method='POST', name='profesores.insertarProfesor')
    def insertarProfesor(self, request):
        '''
        Introduce un nuevo profesor en el sistema.

        Ejemplo de llamada en terminal:
        curl -i -d "nombre=Juan&apellidos=Azustregui&dni=99&direccion=Calle&localidad=Jerezfrontera&provincia=Granada&fecha_nacimiento=1988-2-6&telefono=699164459" -X POST -G localhost:8001/_ah/api/helloworld/v1/profesores/insertarProfesor


        (-i para ver las cabeceras)

        '''

        if v:
            print nombreMicroservicio
            print "Petición POST a profesores.insertarProfesor"
            print "Contenido de la petición:"
            print str(request)
            print '\n'

        #Si no tenemos todos los atributos entonces enviamos un error de bad request.
        if request.nombre==None or request.apellidos==None or request.dni==None or request.direccion==None or request.localidad==None or request.provincia==None or request.fecha_nacimiento==None or request.telefono==None:
            raise endpoints.BadRequestException('Peticion erronea, faltan datos.')

        #Conformamos la dirección:
        url = "http://%s/" % modules.get_hostname(module=sbd)
        #Añadimos el servicio al que queremos conectarnos.
        url+="profesores"


        #Extraemos lo datos de la petición al endpoints
        form_fields = {
          "nombre": request.nombre,
          "apellidos": request.apellidos,
          "dni": request.dni,
          "direccion": request.direccion,
          "localidad": request.localidad,
          "provincia": request.provincia,
          "fecha_nacimiento": request.fecha_nacimiento,
          "telefono": request.telefono
        }

        if v:
            print "Llamando a: "+url


        #Doc de urlfetch: https://cloud.google.com/appengine/docs/python/refdocs/google.appengine.api.urlfetch
        form_data = urllib.urlencode(form_fields)
        #Realizamos la petición al servicio con los datos pasados al endpoint
        result = urlfetch.fetch(url=url, payload=form_data, method=urlfetch.POST)


        #Infro después de la petición:
        if v:
            print nombreMicroservicio
            print "Resultado de la petición de profesores.insertarProfesor"
            print result.content
            print "Código de estado: "
            print result.status_code
            #print str(result.content['status'])
        json = jsonpickle.decode(result.content)

        if str(result.status_code) == '404':
            raise endpoints.NotFoundException('Alumno con ID %s ya existe en el sistema.' % (request.dni))

        #return MensajeRespuesta(message="Todo OK man!")
        #Mandamos la respuesta que nos devuelve la llamada al microservicio:
        return StatusID(status=json['status'], id=int(json['idProfesor']), statusCode=str(result.status_code))


    @endpoints.method(ID,MensajeRespuesta,path='profesores/delProfesor', http_method='DELETE', name='profesores.delProfesor')
    def delProfesor(self, request):

        '''
        delProfesor()

        #Ejemplo de borrado de un recurso pasando el id de un profesor
        Ubuntu> curl -d "dni=1" -X DELETE -G localhost:8001/_ah/api/helloworld/v1/profesores/delProfesor
        {
         "message": "OK"
        }

        #Ejemplo de ejecución en el caso de no encontrar el recurso:
        Ubuntu> curl -d "dni=1" -X DELETE -G localhost:8001/_ah/api/hellworld/v1/profesor/delProfesor
        {
         "message": "Elemento no encontrado"
        }
        '''

        if v:
            print nombreMicroservicio
            print "Petición al método profesores.delProfesor de APIGateway"
            print "Contenido de la petición:"
            print str(request)
            print '\n'

        #Conformamos la dirección:
        url = "http://%s/" % modules.get_hostname(module=sbd)


        #Extraemos el argumento id de la petición y la añadimos a la URL
        url+='alumnos/'+request.id

        if v:
            print "Llamando a: "+url

        #Realizamos la petición a la url del servicio con el método apropiado.
        result = urlfetch.fetch(url=url, method=urlfetch.DELETE)

        #Infro después de la petición:
        if v:
            print nombreMicroservicio
            print "Resultado de la petición: "
            print result.content
            print "Código de estado: "
            print result.status_code


        #Mandamos la respuesta que nos devuelve la llamada al microservicio:
        return MensajeRespuesta(message=result.content)

    @endpoints.method(ProfesorCompleto,MensajeRespuesta,path='profesores/modProfesorCompleto', http_method='POST', name='profesores.modProfesorCompleto')
    def modificarProfesorCompleto(self, request):
        '''
        Modifica todos los atributos de un profesor, aunque algunos queden igual.
        curl -d "id=1&nombre=Pedro&apellidos=Torrssr&dni=23&direccion=CREalCartuja&localidad=Granada&provincia=Granada&fecha_nacimiento=1988-12-4&telefono=23287282" -i -X POST -G localhost:8001/_ah/api/helloworld/v1/profesores/modProfesorCompleto
        '''

        if v:
            print nombreMicroservicio
            print "Petición POST a alumnos.modAlumnoCompleto"
            print "Contenido de la petición:"
            print str(request)
            print '\n'

        if request.nombre==None or request.apellidos==None or request.dni==None or request.direccion==None or request.localidad==None or request.provincia==None or request.fecha_nacimiento==None or request.telefono==None:
            raise endpoints.BadRequestException('Peticion erronea, faltan datos.')

        url = "http://%s/" % modules.get_hostname(module=sbd)

        #Añadimos el recurso al que queremos conectarnos, colección alumnos / alumno con id concreto.
        url+="profesores/"+request.id

        #Extraemos lo datos de la petición que se reciben aquí en el endpoints
        form_fields = {
          "nombre": request.nombre,
          "apellidos": request.apellidos,
          "dni": request.dni,
          "direccion": request.direccion,
          "localidad": request.localidad,
          "provincia": request.provincia,
          "fecha_nacimiento": request.fecha_nacimiento,
          "telefono": request.telefono
        }

        if v:
            print "Llamando a: "+url

        form_data = urllib.urlencode(form_fields)
        result = urlfetch.fetch(url=url, payload=form_data, method=urlfetch.POST)


        #Infro después de la petición:
        if v:
            print nombreMicroservicio
            print "Resultado de la petición: "
            print result.content
            print "Código de estado: "
            print result.status_code

        #return MensajeRespuesta(message="Todo OK man!")
        #Mandamos la respuesta que nos devuelve la llamada al microservicio:
        return MensajeRespuesta(message=result.content)

    #Métodos de relación con otras entidades.

    @endpoints.method(ID, ListaAlumnos, path='profesores/getAlumnosProfesor', http_method='GET', name='profesores.getAlumnosProfesor')
    def getAlumnosProfesores(self, request):
        '''
        Devuelve una lista con los datos resumidos de los alumnos a los que el profesor con id pasado da clase.
        curl -i -X GET localhost:8001/_ah/api/helloworld/v1/profesores/getAlumnosProfesor?id=1
        '''
        #Transformación de la llamada al endpoints a la llamada a la api rest del servicio.
        if v:
            print ("Ejecución de getAlumnosProfesor en apigateway")

        #Conexión a un microservicio específico:

        module = modules.get_current_module_name()
        instance = modules.get_current_instance_id()
        #Le decimos a que microservicio queremos conectarnos (solo usando el nombre del mismo), GAE descubre su URL solo.
        url = "http://%s/" % modules.get_hostname(module=sbd)

        #Añadimos a la url la coleccion (alumnos), el recurso (alumno dado por su dni) y el recurso anidado de este (profesores)
        url+='profesores/'+str(request.id)+"/alumnos"


        print url

        #Realizamos la petición
        result = urlfetch.fetch(url)

        #Vamos a intentar consumir los datos en JSON y convertirlos a un mensje enviable :)

        print "IMPRESION DE LOS DATOS RECIBIDOS"
        print result.content
        listaAlumnos = jsonpickle.decode(result.content)

        #Creamos un vector
        vectorAlumnos= []
        #Que rellenamos con todo los alumnos de la listaAlumnos
        for alumno in listaAlumnos:
            vectorAlumnos.append(Alumno( nombre=formatText(alumno.get('nombre')), apellidos=formatText(alumno.get('apellidos')), id=str(alumno.get('id'))))

        #Los adaptamos al tipo de mensaje y enviamos
        #return Greeting(message=str(result.content))
        return ListaAlumnos(alumnos=vectorAlumnos)

    @endpoints.method(ID, ListaAsignaturas, path='profesores/getAsignaturasProfesor', http_method='GET', name='profesores.getAsignaturasProfesor')
    def getAsignaturasProfesor(self, request):
        '''
        Devuelve una lista con los datos completos de las asignatuas que el profesor en cuestión imparte.
        Ejemplo de llamada:
        curl -i -X GET localhost:8001/_ah/api/helloworld/v1/profesores/getAsignaturasProfesor?id=1
        '''
        if v:
            print ("Ejecución de getAsignaturasProfesor en apigateway")
        module = modules.get_current_module_name()
        instance = modules.get_current_instance_id()
        url = "http://%s/" % modules.get_hostname(module=sbd)
        url+='profesores/'+request.id+"/asignaturas"
        result = urlfetch.fetch(url)
        if v:
            print result.content
        listaAsignaturas = jsonpickle.decode(result.content)
        print listaAsignaturas
        asignaturasItems= []

        for asignatura in listaAsignaturas:
            asignaturasItems.append( Asignatura( id=str(asignatura.get('id')), nombre=formatText(asignatura.get('nombre')) ) )
        return ListaAsignaturas(asignaturas=asignaturasItems)

    @endpoints.method(ID, ListaClases, path='profesores/getClasesProfesor', http_method='GET', name='profesores.getClasesProfesor')
    def getClasesProfesor(self, request):
        '''
        Devuelve una lista con los datos minimos de las clases a las que ese profesor imparte.
        Ejemplo de llamada:
        curl -i -X GET localhost:8001/_ah/api/helloworld/v1/profesores/getClasesProfesor?id=1
        '''
        if v:
            print ("Ejecución de getClasesProfesor en apigateway")
        module = modules.get_current_module_name()
        instance = modules.get_current_instance_id()
        url = "http://%s/" % modules.get_hostname(module=sbd)
        url+='profesores/'+request.id+"/clases"
        result = urlfetch.fetch(url)
        if v:
            print result.content
        listaClases = jsonpickle.decode(result.content)
        print listaClases
        clasesItems= []
        for clase in listaClases:
            clasesItems.append(Clase(id=str(clase.get('id')),curso=str(clase.get('curso')),grupo=str(clase.get('grupo')),nivel=str(clase.get('nivel'))))
        return ListaClases(clases=clasesItems)

    @endpoints.method(ID, ListaAsociaciones, path='profesores/getAsociacionesProfesor', http_method='GET', name='profesores.getAsociacionesProfesor')
    def getAsociacionesProfesor(self, request):
        '''
        Devuelve una lista con las asociaciones a las que un profesor imparte clase
        Ejemplo de llamada:
        curl -i -X GET localhost:8001/_ah/api/helloworld/v1/profesores/getAsociacionesProfesor?id=1
        '''

        #Info de seguimiento
        if v:
            print nombreMicroservicio
            print " Petición GET a profesores.getAsociacionesProfesor"
            print " request: "+str(request)
            print '\n'

        module = modules.get_current_module_name()
        instance = modules.get_current_instance_id()
        url = "http://%s/" % modules.get_hostname(module=sbd)
        url+='profesores/'+request.id+"/asociaciones"
        result = urlfetch.fetch(url)
        if v:
            print ' RESULTADO de la petición'
            print result.content
        listaAsociaciones = jsonpickle.decode(result.content)
        if v:
            print 'lista asociaciones'
            print listaAsociaciones

        vectorAsociaciones= []
        for asociacion in listaAsociaciones:
            print 'asociacion'
            print asociacion
            vectorAsociaciones.append(Asociacion(id_asociacion=str(asociacion.get('id')),
                                                 id_clase=str(asociacion.get('idClase')),
                                                 id_asignatura=str(asociacion.get('idAsignatura')),
                                                 nombreAsignatura=str(asociacion.get('nombreAsignatura')),
                                                 nombreClase=str(asociacion.get('nombreClase'))
                                                 ))
        return ListaAsociaciones(asociaciones=vectorAsociaciones)


    ##############################################
    #   métodos de ASIGNATURAS                   #
    ##############################################

    @endpoints.method(message_types.VoidMessage, ListaAsignaturas, path='asignaturas/getAsignaturas', http_method='GET', name='asignaturas.getAsignaturas')
    def getAsignaturas(self, unused_request):
        '''
        Devuelve una lista con todos las asignaturas registrados en el sistema, de forma simplificada (solo nombre y ID)

        Llamada desde terminal:
        curl -X GET localhost:8001/_ah/api/helloworld/v1/asignaturas/getAsignaturas
        Llamada desde JavaScript:
        response = service.asignaturas.getAsignaturas().execute()
        '''
        #Identificación del módulo en el que estamos.
        module = modules.get_current_module_name()
        instance = modules.get_current_instance_id()

        #Leclear decimos a que microservicio queremos conectarnos (solo usando el nombre del mismo), GAE descubre su URL solo.
        url = "http://%s/" % modules.get_hostname(module=sbd)
        #Añadimos el recurso al que queremos conectarnos.
        url+="asignaturas"
        if v:
            print str(url)
        #Al no especificar nada se llama al método GET de la URL.
        result = urlfetch.fetch(url)
        if v:
            print result.content
        listaAsignaturas = jsonpickle.decode(result.content)

        #Creamos un vector
        asignaturasItems= []
        #Que rellenamos con todo los asignaturas de la listaProfesores
        for asignatura in listaAsignaturas:
            asignaturasItems.append(Asignatura( id=str(asignatura.get('id')), nombre=formatText(asignatura.get('nombre')) ))

        #Los adaptamos al tipo de mensaje y enviamos
        #return Greeting(message=str(result.content))
        return ListaAsignaturas(asignaturas=asignaturasItems)

    @endpoints.method(ID, AsignaturaCompleta, path='asignaturas/getAsignatura', http_method='GET', name='asignaturas.getAsignatura')
    def getAsignatura(self,request):
        '''
        Devuelve toda la información de un profesor en caso de estar en el sistema.

        Llamada ejemplo desde terminal:
        curl -X GET localhost:8001/_ah/api/helloworld/v1/asignaturas/getAsignatura?id=1
        '''

        #Info de seguimiento
        if v:
            print nombreMicroservicio
            print "Petición GET a asignaturas.getAsignatura"
            print "request: "+str(request)
            print '\n'

        #Conexión a un microservicio específico:
        module = modules.get_current_module_name()
        instance = modules.get_current_instance_id()

        #Le decimos al microservicio que queremos conectarnos (solo usando el nombre del mismo), GAE descubre su URL solo.
        url = "http://%s/" % modules.get_hostname(module=sbd)

        #Recursos más entidad
        url+='asignaturas/'+request.id

        if v:
            print "Llamando a: "+str(url)

        #Petición al microservicio
        result = urlfetch.fetch(url=url, method=urlfetch.GET)

        print "RESULTADO:"+str(result.status_code)
        #print result.content
        if v:
            print result.status_code
        if str(result.status_code) == '400':
            raise endpoints.BadRequestException('Peticion erronea')

        if str(result.status_code) == '404':
            raise endpoints.NotFoundException('Profesor con ID %s no encontrado.' % (request.id))

        profesor = jsonpickle.decode(result.content)

        #Infro después de la petición:
        if v:
            print nombreMicroservicio
            print "Resultado de la petición: "
            print result.content
            print "\nCódigo de estado: "+str(result.status_code)+'\n'


        #Componemos un mensaje de tipo AlumnoCompleto.
        #Las partes que son enteros las pasamos a string para enviarlos como mensajes de tipo string.
        #Los campos que tengan NULL en la bd no se pasan al tipo message y ese campo queda vaćio y no se muestra.
        asignatura = AsignaturaCompleta(id=str(profesor.get('id')),
                                nombre=profesor.get('nombre')
                                )

        return asignatura

    @endpoints.method(AsignaturaCompleta, StatusID, path='asignaturas/insertarAsignatura', http_method='POST', name='asignaturas.insertarAsignatura')
    def insertarAsignatura(self, request):
        '''
        Introduce un nuevo profesor en el sistema.

        Ejemplo de llamada en terminal:
        curl -i -d "nombre=CienciasExperimentales" -X POST -G localhost:8001/_ah/api/helloworld/v1/asignaturas/insertarAsignatura
        '''

        if v:
            print nombreMicroservicio
            print "Petición POST a asignaturas.insertarAsignatura"
            print "Contenido de la petición:"
            print str(request)
            print '\n'

        #Si no tenemos todos los atributos entonces enviamos un error de bad request.
        if request.nombre==None:
            raise endpoints.BadRequestException('Peticion erronea, faltan datos.')

        #Conformamos la dirección:
        url = "http://%s/" % modules.get_hostname(module=sbd)
        #Añadimos el servicio al que queremos conectarnos.
        url+="asignaturas"


        #Extraemos lo datos de la petición al endpoints
        form_fields = {
          "nombre": formatTextInput(request.nombre)
        }
        if v:
            print 'form_fields:'
            print form_fields
            print "Llamando a: "+url


        #Doc de urlfetch: https://cloud.google.com/appengine/docs/python/refdocs/google.appengine.api.urlfetch
        form_data = urllib.urlencode(form_fields)
        #Realizamos la petición al servicio con los datos pasados al endpoint
        result = urlfetch.fetch(url=url, payload=form_data, method=urlfetch.POST)


        #Infro después de la petición:
        if v:
            print nombreMicroservicio
            print "Resultado de la petición: "
            print result.content
            print "Código de estado: "
            print result.status_code


        json = jsonpickle.decode(result.content)


        #return MensajeRespuesta(message="Todo OK man!")
        #Mandamos la respuesta que nos devuelve la llamada al microservicio:
        return StatusID(status=json['status'], id=int(json['idAsignatura']), statusCode=str(result.status_code))


    @endpoints.method(ID,MensajeRespuesta,path='asignaturas/delAsignatura', http_method='DELETE', name='asignaturas.delAsignatura')
    def delAsignatura(self, request):

        '''
        delProfesor()

        #Ejemplo de borrado de un recurso pasando el id de un profesor
        Ubuntu> curl -d "id=1" -X DELETE -G localhost:8001/_ah/api/helloworld/v1/asignaturas/delAsignatura
        {
         "message": "OK"
        }

        #Ejemplo de ejecución en el caso de no encontrar el recurso:
        Ubuntu> curl -d "dni=1" -X DELETE -G localhost:8001/_ah/api/hellworld/v1/asignaturas/delAsignatura
        {
         "message": "Elemento no encontrado"
        }
        '''

        if v:
            print nombreMicroservicio
            print "Petición al método asignaturas.delAsignatura de APIGateway"
            print "Contenido de la petición:"
            print str(request)
            print '\n'

        #Conformamos la dirección:
        url = "http://%s/" % modules.get_hostname(module=sbd)


        #Extraemos el argumento id de la petición y la añadimos a la URL
        url+='asignaturas/'+request.id

        if v:
            print "Llamando a: "+url

        #Realizamos la petición a la url del servicio con el método apropiado DELETE
        result = urlfetch.fetch(url=url, method=urlfetch.DELETE)

        #Infro después de la petición:
        if v:
            print nombreMicroservicio
            print "Resultado de la petición: "
            print result.content
            print "Código de estado: "
            print result.status_code


        #Mandamos la respuesta que nos devuelve la llamada al microservicio:
        return MensajeRespuesta(message=result.content)

    @endpoints.method(AsignaturaCompleta,MensajeRespuesta,path='asignaturas/modAsignaturaCompleta', http_method='POST', name='asignaturas.modAsignaturaCompleta')
    def modificarAsignaturaCompleta(self, request):
        '''
        Modifica todos los atributos de una asignatura, aunque algunos queden igual.
        curl -d "id=1&nombre=Chinorri" -i -X POST -G localhost:8001/_ah/api/helloworld/v1/asignaturas/modAsignaturaCompleta
        '''

        if v:
            print nombreMicroservicio
            print "Petición POST a asignaturas.modAsignaturaCompleta"
            print "Contenido de la petición:"
            print str(request)
            print '\n'

        if request.nombre==None or request.id==None:
            raise endpoints.BadRequestException('Peticion erronea, faltan datos.')

        url = "http://%s/" % modules.get_hostname(module=sbd)

        #Añadimos el recurso al que queremos conectarnos, colección alumnos / alumno con id concreto.
        url+="asignaturas/"+request.id

        #Extraemos lo datos de la petición que se reciben aquí en el endpoints
        form_fields = {
          "nombre": formatTextInput(request.nombre)
        }

        if v:
            print "Llamando a: "+url

        form_data = urllib.urlencode(form_fields)
        result = urlfetch.fetch(url=url, payload=form_data, method=urlfetch.POST)


        #Infro después de la petición:
        if v:
            print nombreMicroservicio
            print "Resultado de la petición: "
            print result.content
            print "Código de estado: "
            print result.status_code

        return MensajeRespuesta(message=result.content)

    #Métodos de relaciones con otras entidades

    @endpoints.method(ID, ListaAlumnos, path='asignaturas/getAlumnosAsignatura', http_method='GET', name='asignaturas.getAlumnosAsignatura')
    def getAlumnosAsignatura(self, request):
        '''
        Devuelve una lista con los datos resumidos de los alumnos que esta matriculados en esa clase
        curl -i -X GET localhost:8001/_ah/api/helloworld/v1/asignaturas/getAlumnosAsignatura?id=1
        '''
        #Transformación de la llamada al endpoints a la llamada a la api rest del servicio.
        if v:
            print ("Ejecución de getAlumnosAsignatura en apigateway")

        #Conexión a un microservicio específico:

        module = modules.get_current_module_name()
        instance = modules.get_current_instance_id()
        #Le decimos a que microservicio queremos conectarnos (solo usando el nombre del mismo), GAE descubre su URL solo.
        url = "http://%s/" % modules.get_hostname(module=sbd)

        #Añadimos a la url la coleccion (alumnos), el recurso (alumno dado por su dni) y el recurso anidado de este (profesores)
        url+='asignaturas/'+str(request.id)+"/alumnos"


        print url

        #Realizamos la petición
        result = urlfetch.fetch(url)

        #Vamos a intentar consumir los datos en JSON y convertirlos a un mensje enviable :)

        print "IMPRESION DE LOS DATOS RECIBIDOS"
        print result.content
        listaAlumnos = jsonpickle.decode(result.content)

        #Creamos un vector
        vectorAlumnos= []
        #Que rellenamos con todo los alumnos de la listaAlumnos
        for alumno in listaAlumnos:
            vectorAlumnos.append(Alumno( nombre=formatText(alumno.get('nombre')),
                                         apellidos=formatText(alumno.get('apellidos')),
                                         id=str(alumno.get('id'))
                                         )
                                )

        #Los adaptamos al tipo de mensaje y enviamos
        #return Greeting(message=str(result.content))
        return ListaAlumnos(alumnos=vectorAlumnos)

    @endpoints.method(ID, ListaProfesores, path='asignaturas/getProfesoresAsignatura', http_method='GET', name='asignaturas.getProfesoresAsignatura')
    def getProfesoresAsignatura(self, request):
        '''
        Devuelve una lista con los datos simplificados de los profesores que imparten clase en una asignatura.
        Ejemplo de llamada:
        > curl -i -X GET localhost:8001/_ah/api/helloworld/v1/asignaturas/getProfesoresAsignatura?id=1
        '''
        if v:
            print ("Ejecución de getProfesoresAsignatura en apigateway")
        module = modules.get_current_module_name()
        instance = modules.get_current_instance_id()
        url = "http://%s/" % modules.get_hostname(module=sbd)
        url+='asignaturas/'+request.id+"/profesores"
        result = urlfetch.fetch(url)
        if v:
            print result.content
        listaProfesores = jsonpickle.decode(result.content)
        print listaProfesores
        profesoresItems= []
        for profesor in listaProfesores:
            profesoresItems.append( Profesor( id=str(profesor.get('id')), nombre=str(profesor.get('nombre')), apellidos=str(profesor.get('apellidos')) ) )
        return ListaProfesores(profesores=profesoresItems)

    @endpoints.method(ID, ListaClases, path='asignaturas/getClasesAsignatura', http_method='GET', name='asignaturas.getClasesAsignatura')
    def getClasesAsignatura(self, request):
        '''
        Devuelve una lista con los datos minimos de las clases en las que se imparte esa asignatura
        Ejemplo de llamada:
        > curl -i -X GET localhost:8001/_ah/api/helloworld/v1/asignaturas/getClasesAsignatura?id=1
        '''
        if v:
            print ("Ejecución de getClasesProfesor en apigateway")
        module = modules.get_current_module_name()
        instance = modules.get_current_instance_id()
        url = "http://%s/" % modules.get_hostname(module=sbd)
        url+='asignaturas/'+request.id+"/clases"
        result = urlfetch.fetch(url)
        if v:
            print url
            print "Respuesta del microservicio: \n"
            print result.content
            print "\n"
        listaClases = jsonpickle.decode(result.content)
        print listaClases
        clasesItems= []
        for clase in listaClases:
            clasesItems.append(Clase(id=str(clase.get('id')),curso=str(clase.get('curso')),grupo=str(clase.get('grupo')),nivel=str(clase.get('nivel'))))
        return ListaClases(clases=clasesItems)


    ##############################################
    #   métodos de CLASES                        #
    ##############################################

    @endpoints.method(message_types.VoidMessage, ListaClases, path='clases/getClases', http_method='GET', name='clases.getClases')
    def getClases(self, unused_request):
        '''
        Devuelve una lista con todos las clases registrados en el sistema, de forma simplificada, id_clase, curso, grupo y nivel

        Llamada desde terminal:
        curl -X GET localhost:8001/_ah/api/helloworld/v1/clases/getClases
        Llamada desde JavaScript:
        response = service.clases.getClases().execute()
        '''
        #Identificación del módulo en el que estamos.
        module = modules.get_current_module_name()
        instance = modules.get_current_instance_id()

        #Leclear decimos a que microservicio queremos conectarnos (solo usando el nombre del mismo), GAE descubre su URL solo.
        url = "http://%s/" % modules.get_hostname(module=sbd)
        #Añadimos el recurso al que queremos conectarnos.
        url+="clases"
        if v:
            print str(url)
        #Al no especificar nada se llama al método GET de la URL.
        result = urlfetch.fetch(url)
        if v:
            print result.content
        listaClases = jsonpickle.decode(result.content)

        #Creamos un vector
        clasesItems= []
        #Que rellenamos con todo los asignaturas de la listaProfesores
        for clase in listaClases:
            clasesItems.append(Clase( id=str(clase.get('id')), curso=str(clase.get('curso')), grupo=str(clase.get('grupo')), nivel=str(clase.get('nivel')) ))

        return ListaClases(clases=clasesItems)

    @endpoints.method(ID, ClaseCompleta, path='clases/getClase', http_method='GET', name='clases.getClase')
    def getClase(self,request):
        '''
        Devuelve toda la información de una clase en caso de estar en el sistema.

        Llamada ejemplo desde terminal:
        curl -X GET localhost:8001/_ah/api/helloworld/v1/clases/getClase?id=1
        '''

        #Info de seguimiento
        if v:
            print nombreMicroservicio
            print "Petición GET a clases.getClase"
            print "request: "+str(request)
            print '\n'

        #Conexión a un microservicio específico:
        module = modules.get_current_module_name()
        instance = modules.get_current_instance_id()

        #Le decimos al microservicio que queremos conectarnos (solo usando el nombre del mismo), GAE descubre su URL solo.
        url = "http://%s/" % modules.get_hostname(module=sbd)

        #Recursos más entidad
        url+='clases/'+request.id

        if v:
            print "Llamando a: "+str(url)

        #Petición al microservicio
        result = urlfetch.fetch(url=url, method=urlfetch.GET)

        print "RESULTADO:"+str(result.status_code)
        #print result.content
        if v:
            print result.status_code
        if str(result.status_code) == '400':
            raise endpoints.BadRequestException('Peticion erronea')

        if str(result.status_code) == '404':
            raise endpoints.NotFoundException('Clase con ID %s no encontrada.' % (request.id))

        clase = jsonpickle.decode(result.content)

        #Infro después de la petición:
        if v:
            print nombreMicroservicio
            print "Resultado de la petición: "
            print result.content
            print "\nCódigo de estado: "+str(result.status_code)+'\n'


        #Componemos un mensaje de tipo AlumnoCompleto.
        #Las partes que son enteros las pasamos a string para enviarlos como mensajes de tipo string.
        #Los campos que tengan NULL en la bd no se pasan al tipo message y ese campo queda vaćio y no se muestra.
        clase = ClaseCompleta(id=str(clase.get('id')), curso=str(clase.get('curso')), grupo=str(clase.get('grupo')), nivel=str(clase.get('nivel')) )


        return clase

    @endpoints.method(ClaseCompleta, StatusID, path='clases/insertarClase', http_method='POST', name='clases.insertarClase')
    def insertarClase(self, request):
        '''
        Introduce una nueva clase en el sistema.

        Ejemplo de llamada en terminal:
        curl -i -d "curso=4&grupo=B&nivel=Primaria" -X POST -G localhost:8001/_ah/api/helloworld/v1/clases/insertarClase
        '''

        if v:
            print nombreMicroservicio
            print "Petición POST a clases.insertarClase"
            print "Contenido de la petición:"
            print str(request)
            print '\n'

        #Si no tenemos todos los atributos entonces enviamos un error de bad request.
        if request.curso==None or request.grupo==None or request.nivel==None:
            raise endpoints.BadRequestException('Peticion erronea, faltan datos.')

        #Conformamos la dirección:
        url = "http://%s/" % modules.get_hostname(module=sbd)
        #Añadimos el servicio al que queremos conectarnos.
        url+="clases"


        #Extraemos lo datos de la petición al endpoints
        form_fields = {
          "curso": request.curso,
          "grupo": request.grupo,
          "nivel": request.nivel,
        }

        if v:
            print "Llamando a: "+url


        #Doc de urlfetch: https://cloud.google.com/appengine/docs/python/refdocs/google.appengine.api.urlfetch
        form_data = urllib.urlencode(form_fields)
        #Realizamos la petición al servicio con los datos pasados al endpoint
        result = urlfetch.fetch(url=url, payload=form_data, method=urlfetch.POST)


        #Infro después de la petición:
        if v:
            print nombreMicroservicio
            print "Resultado de la petición: "
            print result.content
            print "Código de estado: "
            print result.status_code


        json = jsonpickle.decode(result.content)

        #Mandamos la respuesta que nos devuelve la llamada al microservicio:
        return StatusID(status=json['status'], id=int(json['idClase']), statusCode=str(result.status_code))


    @endpoints.method(ID,MensajeRespuesta,path='clases/delClase', http_method='DELETE', name='clases.delClase')
    def delClase(self, request):

        '''
        Elimina la clase con id pasado en caso de existir en el sistema.

        #Ejemplo de borrado de un recurso pasando el id de la clase.
        Ubuntu> curl -d "id=1" -X DELETE -G localhost:8001/_ah/api/helloworld/v1/clases/delClase
        {
         "message": "OK"
        }
        '''

        if v:
            print nombreMicroservicio
            print "Petición al método clases.delClase de APIGateway"
            print "Contenido de la petición:"
            print str(request)
            print '\n'

        #Conformamos la dirección:
        url = "http://%s/" % modules.get_hostname(module=sbd)


        #Extraemos el argumento id de la petición y la añadimos a la URL
        url+='clases/'+request.id

        if v:
            print "Llamando a: "+url

        #Realizamos la petición a la url del servicio con el método apropiado DELETE
        result = urlfetch.fetch(url=url, method=urlfetch.DELETE)

        #Infro después de la petición:
        if v:
            print nombreMicroservicio
            print "Resultado de la petición: "
            print result.content
            print "Código de estado: "
            print result.status_code


        #Mandamos la respuesta que nos devuelve la llamada al microservicio:
        return MensajeRespuesta(message=result.content)

    @endpoints.method(ClaseCompleta, MensajeRespuesta, path='clases/modClaseCompleta', http_method='POST', name='clases.modClaseCompleta')
    def modificarClaseCompleta(self, request):
        '''
        Modifica todos los atributos de una clase, aunque algunos queden igual.
        curl -d "id=1&curso=1&grupo=B&nivel=BACH" -i -X POST -G localhost:8001/_ah/api/helloworld/v1/clases/modClaseCompleta
        '''

        if v:
            print nombreMicroservicio
            print "Petición POST a clases.modClaseCompleta"
            print "Contenido de la petición:"
            print str(request)
            print '\n'

        if  request.id==None or request.curso==None or request.grupo==None or request.nivel==None:
            raise endpoints.BadRequestException('Peticion erronea, faltan datos.')

        url = "http://%s/" % modules.get_hostname(module=sbd)

        #Añadimos el recurso al que queremos conectarnos, colección alumnos / alumno con id concreto.
        url+="clases/"+request.id

        #Extraemos lo datos de la petición que se reciben aquí en el endpoints
        form_fields = {
          "curso": request.curso,
          "grupo": request.grupo,
          "nivel": request.nivel
        }

        if v:
            print "Llamando a: "+url

        form_data = urllib.urlencode(form_fields)
        result = urlfetch.fetch(url=url, payload=form_data, method=urlfetch.POST)


        #Infro después de la petición:
        if v:
            print nombreMicroservicio
            print "Resultado de la petición: "
            print result.content
            print "Código de estado: "
            print result.status_code

        return MensajeRespuesta(message=result.content)

    #Métodos de relaciones con otras entidades

    @endpoints.method(ID, ListaAlumnos, path='clases/getAlumnosClase', http_method='GET', name='clases.getAlumnosClase')
    def getAlumnosClase(self, request):
        '''
        Devuelve una lista con los datos resumidos de los alumnos que esta matriculados en esa clase
        curl -i -X GET localhost:8001/_ah/api/helloworld/v1/clases/getAlumnosClase?id=1
        '''
        #Transformación de la llamada al endpoints a la llamada a la api rest del servicio.
        if v:
            print ("Ejecución de getAlumnosClase en apigateway")

        module = modules.get_current_module_name()
        instance = modules.get_current_instance_id()
        url = "http://%s/" % modules.get_hostname(module=sbd)
        url+='clases/'+str(request.id)+"/alumnos"

        if v:
            print url

        #Realizamos la petición
        result = urlfetch.fetch(url)

        if v:
            print "IMPRESION DE LOS DATOS RECIBIDOS"
            print result.content
        listaAlumnos = jsonpickle.decode(result.content)
        vectorAlumnos= []
        for alumno in listaAlumnos:
            vectorAlumnos.append(Alumno( id=str(alumno.get('id')), nombre=formatText(alumno.get('nombre')), apellidos=formatText(alumno.get('apellidos'))))
        return ListaAlumnos(alumnos=vectorAlumnos)

    @endpoints.method(ID, ListaProfesores, path='clases/getProfesoresClase', http_method='GET', name='clases.getProfesoresClase')
    def getProfesoresClase(self, request):
        '''
        Devuelve una lista con los datos simplificados de los profesores que imparten alguna asignatura a esa clase.
        Ejemplo de llamada:
        curl -i -X GET localhost:8001/_ah/api/helloworld/v1/clases/getProfesoresClase?id=1
        '''
        if v:
            print ("Ejecución de getProfesoresAsignatura en apigateway")
        module = modules.get_current_module_name()
        instance = modules.get_current_instance_id()
        url = "http://%s/" % modules.get_hostname(module=sbd)
        url+='clases/'+request.id+"/profesores"
        result = urlfetch.fetch(url)
        if v:
            print result.content
        listaProfesores = jsonpickle.decode(result.content)
        print listaProfesores
        profesoresItems= []
        for profesor in listaProfesores:
            profesoresItems.append( Profesor( id=str(profesor.get('id')), nombre=formatText(profesor.get('nombre')), apellidos=formatText(profesor.get('apellidos')) ) )
        return ListaProfesores(profesores=profesoresItems)

    @endpoints.method(ID, ListaAsignaturas, path='clases/getAsignaturasClase', http_method='GET', name='clases.getAsignaturasClase')
    def getAsignaturasClase(self, request):
        '''
        Devuelve una lista con los datos mínimos de las asignaturas que se imparten en una clase.
        Ejemplo de llamada:
        > curl -i -X GET localhost:8001/_ah/api/helloworld/v1/clases/getAsignaturasClase?id=1
        '''
        if v:
            print ("Ejecución de getAsignaturasProfesor en apigateway")
        module = modules.get_current_module_name()
        instance = modules.get_current_instance_id()
        url = "http://%s/" % modules.get_hostname(module=sbd)
        url+='clases/'+request.id+"/asignaturas"
        result = urlfetch.fetch(url)
        if v:
            print result.content
        listaAsignaturas = jsonpickle.decode(result.content)
        print listaAsignaturas
        asignaturasItems= []
        for asignatura in listaAsignaturas:
            asignaturasItems.append( Asignatura( id=str(asignatura.get('id')), nombre=formatText(asignatura.get('nombre')) ) )
        return ListaAsignaturas(asignaturas=asignaturasItems)

    @endpoints.method(ID, ListaAsociaciones, path='clases/getAsociacionesClase', http_method='GET', name='clases.getAsociacionesClase')
    def getAsociacionesClase(self, request):
        '''
            curl -i -X GET localhost:8001/_ah/api/helloworld/v1/clases/getAsociacionesClase?id=1
        '''
        if v:
            print ("Ejecución de getAsociacionesClase en apigateway")
        module = modules.get_current_module_name()
        instance = modules.get_current_instance_id()
        url = "http://%s/" % modules.get_hostname(module=sbd)
        url+='clases/'+request.id+"/asociaciones"
        result = urlfetch.fetch(url)
        if v:
            print result.content
        listaAsociaciones = jsonpickle.decode(result.content)
        print listaAsociaciones
        listaAS= []

        for a in listaAsociaciones:
            listaAS.append( Asociacion( id_asociacion=str(a.get('id')), id_clase=str(a.get('idClase')), id_asignatura=str(a.get('idAsignatura')), nombreAsignatura=formatText(a.get('nombreAsignatura')) ) )
        return ListaAsociaciones(asociaciones=listaAS)

    ##############################################
    #   métodos de MATRICULAS                    #
    ##############################################

    @endpoints.method(message_types.VoidMessage, ListaMatriculas, path='matriculas/getMatriculas', http_method='GET', name='matriculas.getMatriculas')
    def getMatriculas(self, unused_request):
        '''
        Devuelve una lista con todos las matriculas registrados en el sistema.

        Llamada desde terminal:
        curl -X GET localhost:8001/_ah/api/helloworld/v1/matriculas/getMatriculas
        Llamada desde JavaScript:
        response = service.matriculas.getMatriculas().execute()
        '''
        #Identificación del módulo en el que estamos.
        module = modules.get_current_module_name()
        instance = modules.get_current_instance_id()

        #Leclear decimos a que microservicio queremos conectarnos (solo usando el nombre del mismo), GAE descubre su URL solo.
        url = "http://%s/" % modules.get_hostname(module=sbd)
        #Añadimos el recurso al que queremos conectarnos.
        url+="matriculas"
        if v:
            print str(url)
        #Al no especificar nada se llama al método GET de la URL.
        result = urlfetch.fetch(url)
        if v:
            print result.content
        listaMatriculas = jsonpickle.decode(result.content)

        #Creamos un vector
        matriculasItems= []

        for matricula in listaMatriculas:
            matriculasItems.append(Matricula( id_matricula=str(matricula.get('id')),
                                              id_alumno=str(matricula.get('id_alumno')),
                                              id_asociacion=str(matricula.get('id_asociacion'))
                                            ))

        return ListaMatriculas(matriculas=matriculasItems)

    @endpoints.method(Matricula, MensajeRespuesta, path='matriculas/insertarMatricula', http_method='POST', name='matriculas.insertarMatricula')
    def insertarMatricula(self, request):
        '''
        Introduce una nueva clase en el sistema.

        Ejemplo de llamada en terminal:
        curl -i -d "id_alumno=2&id_asociacion=2" -X POST -G localhost:8001/_ah/api/helloworld/v1/matriculas/insertarMatricula
        '''

        if v:
            print nombreMicroservicio
            print "Petición POST a clases.insertarClase"
            print "Contenido de la petición:"
            print str(request)
            print '\n'

        #Si no tenemos todos los atributos entonces enviamos un error de bad request.
        if request.id_alumno==None or request.id_asociacion==None:
            raise endpoints.BadRequestException('Peticion erronea, faltan datos.')

        #Conformamos la dirección:
        url = "http://%s/" % modules.get_hostname(module=sbd)
        #Añadimos el servicio al que queremos conectarnos.
        url+="matriculas"


        #Extraemos lo datos de la petición al endpoints
        form_fields = {
          "id_alumno": request.id_alumno,
          "id_asociacion": request.id_asociacion
        }

        if v:
            print "Llamando a: "+url


        #Doc de urlfetch: https://cloud.google.com/appengine/docs/python/refdocs/google.appengine.api.urlfetch
        form_data = urllib.urlencode(form_fields)
        #Realizamos la petición al servicio con los datos pasados al endpoint
        result = urlfetch.fetch(url=url, payload=form_data, method=urlfetch.POST)


        #Infro después de la petición:
        if v:
            print nombreMicroservicio
            print "Resultado de la petición: "
            print result.content
            print "Código de estado: "
            print result.status_code

        return MensajeRespuesta(message=result.content)

    @endpoints.method(ID,MensajeRespuesta,path='matriculas/delMatricula', http_method='DELETE', name='matriculas.delMatricula')
    def delMatricula(self, request):

        '''
        Elimina una matriculación en el sistema, identificándola con su id.

        #Ejemplo de borrado de una matrícula:
        curl -d "id=2" -X DELETE -G localhost:8001/_ah/api/helloworld/v1/matriculas/delMatricula
        {
         "message": "OK"
        }
        '''

        if v:
            print nombreMicroservicio
            print "Petición al método clases.delClase de APIGateway"
            print "Contenido de la petición:"
            print str(request)
            print '\n'

        #Conformamos la dirección:
        url = "http://%s/" % modules.get_hostname(module=sbd)


        #Extraemos el argumento id de la petición y la añadimos a la URL
        url+='matriculas/'+request.id

        if v:
            print "Llamando a: "+url

        #Realizamos la petición a la url del servicio con el método apropiado DELETE
        result = urlfetch.fetch(url=url, method=urlfetch.DELETE)

        #Infro después de la petición:
        if v:
            print nombreMicroservicio
            print "Resultado de la petición: "
            print result.content
            print "Código de estado: "
            print result.status_code


        #Mandamos la respuesta que nos devuelve la llamada al microservicio:
        return MensajeRespuesta(message=result.content)

    ##############################################
    #   métodos de IMPARTE                       #
    ##############################################

    @endpoints.method(message_types.VoidMessage, ListaImpartes, path='impartes/getImpartes', http_method='GET', name='impartes.getImpartes')
    def getImpartes(self, unused_request):
        '''
        Devuelve una lista con todos las entidades de la relación Imparte del sistema.
        Llamada desde terminal:
        curl -X GET localhost:8001/_ah/api/helloworld/v1/impartes/getImpartes
        '''
        module = modules.get_current_module_name()
        instance = modules.get_current_instance_id()
        #Leclear decimos a que microservicio queremos conectarnos (solo usando el nombre del mismo), GAE descubre su URL solo.
        url = "http://%s/" % modules.get_hostname(module=sbd)
        #Añadimos el recurso al que queremos conectarnos.
        url+="impartes"
        if v:
            print str(url)
        #Al no especificar nada se llama al método GET de la URL.
        result = urlfetch.fetch(url)
        if v:
            print result.content
        listaImpartes = jsonpickle.decode(result.content)

        #Creamos un vector
        impartesItems= []

        for imparte in listaImpartes:
            impartesItems.append(Imparte( id_profesor=str(imparte.get('id_profesor')),
                                              id_clase=str(imparte.get('id_clase')),
                                              id_asignatura=str(imparte.get('id_asignatura'))
                                            ))

        return ListaImpartes(impartes=impartesItems)

    @endpoints.method(Imparte, MensajeRespuesta, path='impartes/insertarImparte', http_method='POST', name='impartes.insertarImparte')
    def insertarImparte(self, request):
        '''
        Introduce una relación Imparte (un procesor que imaparte una asignatura en una clase).
        Ejemplo de llamada en terminal:
        curl -i -d "id_asociacion=1&id_profesor=2" -X POST -G localhost:8001/_ah/api/helloworld/v1/impartes/insertarImparte
        '''

        if v:
            print nombreMicroservicio
            print "Petición POST a impartes.insertarImparte"
            print "Contenido de la petición:"
            print str(request)
            print '\n'

        #Si no tenemos todos los atributos entonces enviamos un error de bad request.
        if request.id_profesor==None or request.id_asociacion==None:
            raise endpoints.BadRequestException('Peticion erronea, faltan datos.')

        #Conformamos la dirección:
        url = "http://%s/" % modules.get_hostname(module=sbd)
        #Añadimos el servicio al que queremos conectarnos.
        url+="impartes"


        #Extraemos lo datos de la petición al endpoints
        form_fields = {
          "id_profesor": request.id_profesor,
          "id_asociacion": request.id_asociacion,
        }

        if v:
            print "Llamando a: "+url


        #Doc de urlfetch: https://cloud.google.com/appengine/docs/python/refdocs/google.appengine.api.urlfetch
        form_data = urllib.urlencode(form_fields)
        #Realizamos la petición al servicio con los datos pasados al endpoint
        result = urlfetch.fetch(url=url, payload=form_data, method=urlfetch.POST)


        #Infro después de la petición:
        if v:
            print nombreMicroservicio
            print "Resultado de la petición: "
            print result.content
            print "Código de estado: "
            print result.status_code

        return MensajeRespuesta(message=result.content)

    @endpoints.method(ID,MensajeRespuesta,path='impartes/delImparte', http_method='DELETE', name='impartes.delImparte')
    def delImparte(self, request):

        '''
        Elimina una tupla de la relación Imparte del sistema.

        #Ejemplo de borrado de una matrícula:
        curl -d "id=2" -X DELETE -G localhost:8001/_ah/api/helloworld/v1/impartes/delImparte
        {
         "message": "OK"
        }
        '''

        if v:
            print nombreMicroservicio
            print "Petición al método clases.delClase de APIGateway"
            print "Contenido de la petición:"
            print str(request)
            print '\n'

        #Conformamos la dirección:
        url = "http://%s/" % modules.get_hostname(module=sbd)


        #Extraemos el argumento id de la petición y la añadimos a la URL
        url+='impartes/'+request.id

        if v:
            print "Llamando a: "+url

        #Realizamos la petición a la url del servicio con el método apropiado DELETE
        result = urlfetch.fetch(url=url, method=urlfetch.DELETE)

        #Infro después de la petición:
        if v:
            print nombreMicroservicio
            print "Resultado de la petición: "
            print result.content
            print "Código de estado: "
            print result.status_code


        #Mandamos la respuesta que nos devuelve la llamada al microservicio:
        return MensajeRespuesta(message=result.content)

    ##############################################
    #   métodos de ASOCIA                       #
    ##############################################

    @endpoints.method(message_types.VoidMessage, ListaAsociaciones, path='asociaciones/getAsociaciones', http_method='GET', name='asociaciones.getAsociaciones')
    def getAsociaciones(self, unused_request):
        '''
        Devuelve una lista con todos las entidades de la relación Asocia del sistema.
        Llamada desde terminal:
        curl -X GET localhost:8001/_ah/api/helloworld/v1/asociaciones/getAsociaciones
        '''
        module = modules.get_current_module_name()
        instance = modules.get_current_instance_id()
        #Leclear decimos a que microservicio queremos conectarnos (solo usando el nombre del mismo), GAE descubre su URL solo.
        url = "http://%s/" % modules.get_hostname(module=sbd)
        #Añadimos el recurso al que queremos conectarnos.
        url+="asociaciones"
        if v:
            print str(url)
        #Al no especificar nada se llama al método GET de la URL.
        result = urlfetch.fetch(url)
        if v:
            print result.content
        listaAsociaciones = jsonpickle.decode(result.content)

        #Creamos un vector
        asociacionesItems= []

        for asociacion in listaAsociaciones:
            asociacionesItems.append(Asociacion( id_asociacion=str(asociacion.get('id')),
                                                 id_clase=str(asociacion.get('id_clase')),
                                                 id_asignatura=str(asociacion.get('id_asignatura'))
                                               ))

        return ListaAsociaciones(asociaciones=asociacionesItems)

    @endpoints.method(Asociacion, MensajeRespuesta, path='asociaciones/insertaAsociacion', http_method='POST', name='asociaciones.insertaAsociacion')
    def insertarAsociacion(self, request):
        '''
        Introduce una relación Asocia (una especificación de una asignatura en una clase concreta).
        Ejemplo de llamada en terminal:
        curl  -d "id_asignatura=2&id_clase=3" -X POST -G localhost:8001/_ah/api/helloworld/v1/asociaciones/insertaAsociacion
        '''

        if v:
            print nombreMicroservicio
            print "Petición POST a asociaciones.insertaAsociacion"
            print "Contenido de la petición:"
            print str(request)
            print '\n'

        #Si no tenemos todos los atributos entonces enviamos un error de bad request.
        if request.id_asignatura==None or request.id_clase==None:
            raise endpoints.BadRequestException('Peticion erronea, faltan datos.')

        #Conformamos la dirección:
        url = "http://%s/" % modules.get_hostname(module=sbd)
        #Añadimos el servicio al que queremos conectarnos.
        url+="asociaciones"


        #Extraemos lo datos de la petición al endpoints
        form_fields = {
          "id_asignatura": request.id_asignatura,
          "id_clase": request.id_clase,
        }

        if v:
            print "Llamando a: "+url


        #Doc de urlfetch: https://cloud.google.com/appengine/docs/python/refdocs/google.appengine.api.urlfetch
        form_data = urllib.urlencode(form_fields)
        #Realizamos la petición al servicio con los datos pasados al endpoint
        result = urlfetch.fetch(url=url, payload=form_data, method=urlfetch.POST)


        #Infro después de la petición:
        if v:
            print nombreMicroservicio
            print "Resultado de la petición: "
            print result.content
            print "Código de estado: "
            print result.status_code

        return MensajeRespuesta(message=result.content)

    @endpoints.method(ID,MensajeRespuesta,path='asociaciones/delImparte', http_method='DELETE', name='asociaciones.delImparte')
    def delAsociacion(self, request):

        '''
        Elimina una tupla de la relación Imparte del sistema.

        #Ejemplo de borrado de una matrícula:
        curl -d "id=2" -X DELETE -G localhost:8001/_ah/api/helloworld/v1/impartes/delImparte
        {
         "message": "OK"
        }
        '''

        if v:
            print nombreMicroservicio
            print "Petición al método clases.delClase de APIGateway"
            print "Contenido de la petición:"
            print str(request)
            print '\n'

        #Conformamos la dirección:
        url = "http://%s/" % modules.get_hostname(module=sbd)


        #Extraemos el argumento id de la petición y la añadimos a la URL
        url+='impartes/'+request.id

        if v:
            print "Llamando a: "+url

        #Realizamos la petición a la url del servicio con el método apropiado DELETE
        result = urlfetch.fetch(url=url, method=urlfetch.DELETE)

        #Infro después de la petición:
        if v:
            print nombreMicroservicio
            print "Resultado de la petición: "
            print result.content
            print "Código de estado: "
            print result.status_code


        #Mandamos la respuesta que nos devuelve la llamada al microservicio:
        return MensajeRespuesta(message=result.content)

    @endpoints.method(ID, AsociacionCompleta,path='asociaciones/getAsociacionCompleta', http_method='GET', name='asociaciones.getAsociacionCompleta')
    def getAsociacionCompleta(self, request):

        '''
        curl -X GET localhost:8001/_ah/api/helloworld/v1/asociaciones/getAsociacionCompleta?id=1
        '''

        module = modules.get_current_module_name()
        instance = modules.get_current_instance_id()
        #Leclear decimos a que microservicio queremos conectarnos (solo usando el nombre del mismo), GAE descubre su URL solo.
        url = "http://%s/" % modules.get_hostname(module=sbd)
        #Añadimos el recurso al que queremos conectarnos.
        url+="asociaciones/"+request.id
        if v:
            print str(url)
        #Al no especificar nada se llama al método GET de la URL.
        result = urlfetch.fetch(url)
        if v:
            print result.content

        #Información Asociación Completa
        iac = jsonpickle.decode(result.content)

        print 'IAC recibido: \n'
        print iac

        #Formateamos la información recibida para enviarla.

        #Creamos un par de vectores
        profesores= []
        alumnos = []


        for profesor in iac['profesoresAsociacion']:
            profesores.append(ProfesorSimpleExtendido( nombre=formatText(profesor.get('nombre')), apellidos=formatText(profesor.get('apellidos')), id=str(profesor.get('id')), idImparte=str(profesor.get('idImparte')) ))

        for alumno in iac['alumnosAsociacion']:
            alumnos.append(AlumnoSimpleExtendido( nombre=formatText(alumno.get('nombre')), apellidos=formatText(alumno.get('apellidos')), id=str(alumno.get('id')), idMatricula=str(alumno.get('idMatricula'))))

        return AsociacionCompleta( nombreAsignatura=formatText(iac['nombreAsignatura']), listaProfesores=profesores, listaAlumnos=alumnos, idAsociacion=request.id)

    #Relación con otras entidades.

    @endpoints.method(ID, ListaAlumnos, path='asociaciones/getAlumnos', http_method='GET', name='asociaciones.getAlumnos')
    def getAlumnosAsociacion(self, request):
        '''
        Devuelve una lista con todos los alumnos matriculados a una asociacion (Asignatura-Clase) específica.
        curl -X GET localhost:8001/_ah/api/helloworld/v1/asociaciones/getAlumnos?id=1
        '''

        #Info de seguimiento
        if v:
            print nombreMicroservicio
            print ' Petición GET a asociaciones.getAlumnos'
            print ' Request: \n '+str(request)+'\n'


        module = modules.get_current_module_name()
        instance = modules.get_current_instance_id()
        #Leclear decimos a que microservicio queremos conectarnos (solo usando el nombre del mismo), GAE descubre su URL solo.
        url = "http://%s/" % modules.get_hostname(module=sbd)
        #Añadimos el recurso al que queremos conectarnos.
        url+="asociaciones/"+request.id+"/alumnos"
        result = urlfetch.fetch(url)
        respuestaMServicio= jsonpickle.decode(result.content)
        #Creamos un array de alumnos
        vector_alumnos = []

        for alumno in respuestaMServicio:
            idAlumno = str(alumno.get('id'))
            nombreAlumno = alumno.get('nombre')
            apellidosAlumno = alumno.get('apellidos')
            vector_alumnos.append(Alumno( id=idAlumno, nombre=formatText(nombreAlumno), apellidos=formatText(apellidosAlumno) ) )


        #Info de seguimiento
        if v:
            print nombreMicroservicio
            print ' Respuesta de asociaciones.getAlumnos'
            print ' Return: '+str(vector_alumnos)+'\n'

        return ListaAlumnos(alumnos=vector_alumnos)




    ##############################################
    #   métodos de CONTROL DE ESTUDIANTES        #
    #               mServicio SCE                #
    ##############################################


    #@endpoints.method(message_types.VoidMessage, ListaResumenControlAsistencia )
    #def getAllResumenesControlAsistencia(self, request):


    #La url hay que mejorarla no necesita el /insertarControl (se identifica con el método)
    @endpoints.method(ListaControlAsistencia, MensajeRespuesta, path='controles/insertarControl', http_method='POST', name='controles.insertarControl')
    def subirControl(self, request):
        '''
        Permite subir una lista de controles de asistencia.
        '''
        #Info de seguimiento
        if v:
            print nombreMicroservicio
            print ' Petición POST a controles.insertarControl'
            print ' Request: \n '+str(request)+'\n'
            print ' Request-CONTROLES: \n '+str(request.controles)+'\n'


        #Parseo de los datos en formato message de RPC a JSON enviable a los microservicios a través del urlfetch (seguro que hay una forma mas bonita de hacerlo)

        #Creamos un diciconario con una lista dentro llamada controles.
        diccionario = { 'controles': []}
        '''
        Recorremos los controles que nos envían en el mensaje ListaControlAsistencia. Esto podemos hacerlo porque el formato de mensaje es
        class ListaControlAsistencia(messages.Message):
            controles = messages.MessageField(ControlAsistencia, 1, repeated=True)
        '''
        for a in request.controles:
            #Creamos un diccionario por cada elemento dentro de controles, que es de tipo ControlAsistencia
            tmpDic = {}
            #Extraemos los datos y los insertarmos en el dic
            tmpDic['asistencia'] = a.asistencia
            tmpDic['retraso'] = a.retraso
            #tmpDic['retrasoTiempo'] = a.retrasoTiempo
            tmpDic['retrasoJustificado'] = a.retrasoJustificado
            tmpDic['uniforme'] = a.uniforme
            tmpDic['idAlumno'] = a.id


            #Los tres restantes vienen por la PARTE COMÚN (no en los controles)
            tmpDic['idProfesor'] = request.idProfesor
            tmpDic['idClase'] = request.idClase
            tmpDic['idAsignatura'] = request.idAsignatura
            #A partir de este momento se incrustan en cada control

            #Añadimo este tmpDic a la lista controles del diccionario principal.
            diccionario['controles'].append(tmpDic)

        #Usamos la librería json para terminar de darle formato y listo para usar.
        jsonData = json.dumps(diccionario)
        #Fin del proceso de conversión.


        #Conformamos la dirección:
        url = "http://%s/" % modules.get_hostname(module="sce")
        #Añadimos el metodo al que queremos conectarnos.
        url+="controlesAsistencia"

        #Petición al microservicio, pasándole como payload los datos recibidos aquí en el endpoint
        result = urlfetch.fetch(url=url, payload=jsonData, method=urlfetch.POST, headers = {"Content-Type": "application/json"})

        print ' Status code from microservice response: '+str(result.status_code)


        #Info de seguimiento
        if v:
            print nombreMicroservicio
        #print ' Respuesta de controles.insertarControl '+str(result)

        return MensajeRespuesta( message='yeah' )


    @endpoints.method(ParametrosPeticionResumen, ListaResumenControlAsistencia, path='controles/resumenes', http_method='GET', name='controles.getResumenes')
    def getResumenesControlesAsistenciaConParametros(self, request):
        '''
        Devuelve una lista con todos los resumenes de los controles de estudiantes almacenados en el sistema filtrados
        por cualquiera de los campos.

        curl -X GET localhost:8001/_ah/api/helloworld/v1/controles/resumenes?idProfesor=4


        class ResumenControlAsistencia(messages.Message):
            key = messages.StringField(1, required=True)
            fecha = messages.StringField(2)
            idClase = messages.StringField(3)
            nombreClase = messages.StringField(4)
            idAsignatura = messages.StringField(5)
            nombreAsignatura = messages.StringField(6)
            idProfesor = messages.StringField(7)
            nombreProfesor = messages.StringField(8)

        class ListaResumenControlAsistencia(messages.Message):
            resumenes = messages.MessageField(ResumenControlAsistencia, 1, repeated=True)

        #Cuando pedimos los resumenes de los controles de asistencia los podemos pedir usando parámetros o sin ellos.
        class ParametrosPeticionResumen(messages.Message):
            idProfesor = messages.IntegerField(1)
            idAsignatura = messages.IntegerField(2)
            idClase = messages.IntegerField(3)
            fechaHora = messages.StringFiedl(4)

        '''
        #Info de seguimiento
        if v:
            print nombreMicroservicio
            print ' Petición POST a controles.getResumenes'
            print ' Request: \n '+str(request)+'\n'



        #Conformamos la dirección:
        url = "http://%s/" % modules.get_hostname(module="sce")
        url+="resumenesControlesAsistenciaEspecificos"


        #Extraemos los datos pasados a la petición y los empaquetamos en un dict.

        #Creamos un diccionario
        datos = {}

        #Si viene por parámetro el id del profesor lo añadimos al diccionario
        if request.idProfesor != None:
            datos['idProfesor']=request.idProfesor
        #Hacemos lo mismo con el resto:
        if request.idAsignatura != None:
            datos['idAsignatura']=request.idAsignatura
        if request.idClase != None:
            datos['idClase']=request.idClase
        if request.fechaHora != None:
            datos['fechaHora']=request.fechaHora

        #Vemos como queda datos
        print datos

        #Petición al microservicio:
        result = urlfetch.fetch(url=url, payload=urllib.urlencode(datos), method=urlfetch.POST)
        listaResumenes = jsonpickle.decode(result.content)
        print 'Resultado'
        print listaResumenes


        '''
        class ResumenControlAsistencia(messages.Message):
            key = messages.StringField(1, required=True)
            fecha = messages.StringField(2)
            idClase = messages.StringField(3)
            nombreClase = messages.StringField(4)
            idAsignatura = messages.StringField(5)
            nombreAsignatura = messages.StringField(6)
            idProfesor = messages.StringField(7)
            nombreProfesor = messages.StringField(8)

        class ListaResumenControlAsistencia(messages.Message):
            resumenes = messages.MessageField(ResumenControlAsistencia, 1, repeated=True)
        '''

        resumenesItems= []

        for resumen in listaResumenes:
            print 'RESUMEN'
            print resumen
            print 'nombreClase'
            print resumen.get('nombreClase')


            resumenesItems.append( ResumenControlAsistencia( key=int(resumen.get('key')),
                                                             fecha=str(resumen.get('fecha')),
                                                             idClase=int(resumen.get('idClase')),
                                                             nombreClase=formatText(resumen.get('nombreClase')),
                                                             idAsignatura=int(resumen.get('idAsignatura')),
                                                             nombreAsignatura=formatText(resumen.get('nombreAsignatura')),
                                                             idProfesor=int(resumen.get('idProfesor')),
                                                             nombreProfesor=formatText(resumen.get('nombreProfesor'))
                                                           ))

        # Pequeño delay para pruebas con el css
        import time
        time.sleep(2)


        return ListaResumenControlAsistencia(resumenes=resumenesItems)



        #return MensajeRespuesta(message="Hola ke ase!")

    #La url hay que mejorarla, no necesita el /getControl (Se identifica con el método)
    @endpoints.method(ID, ListaControlAsistencia, path='controles/getControl', http_method='GET', name='controles.getControl')
    def getControlAsistencia(self, request):
        '''

        curl -X GET localhost:8001/_ah/api/helloworld/v1/controles/getControl?id=4644337115725824

        Devuelve un control de asistencia completo que se le pide con el id pasado.
        '''
        #Info de seguimiento
        if v:
            print nombreMicroservicio
            print ' Petición POST a controles.getContol'
            print ' Request: \n '+str(request)+'\n'



        #Conformamos la dirección:
        url = "http://%s/" % modules.get_hostname(module="sce")
        url+="controlAsistencia/"+request.id

        if v:
            print "Llamando a: "+str(url)

        #Petición al microservicio
        result = urlfetch.fetch(url=url, method=urlfetch.GET)

        print "RESULTADO:"+str(result.status_code)

        #Convertimos el json a un objeto python
        controlAsistencia = jsonpickle.decode(result.content)

        print 'controlAsistencia'
        print controlAsistencia

        #Convertirmos este objeto python al mensja de rpc para ser enviado.

        resumenesItems= []

        #Recorremos todos los elementos de la lista 'controles' del diccionario devuelto por el mservicio sce.
        listaControles = []
        for mControl in controlAsistencia['controles']:
            #print 'mControl'
            #print mControl
            listaControles.append(ControlAsistencia( asistencia=int(mControl['asistencia']),
                                                     retraso=int(mControl['retraso']),
                                                     retrasoJustificado=int(mControl['retrasoJustificado']),
                                                     uniforme=int(mControl['uniforme']),
                                                     nombreAlumno=formatText(mControl['nombreAlumno']),
                                                     id=int(mControl['idAlumno'])
                                                   ))

        #Una vez que tenemos la lista componemos el mensaje final
        return ListaControlAsistencia( controles=listaControles,
                                       idProfesor=int(controlAsistencia['idProfesor']),
                                       idClase=int(controlAsistencia['idClase']),
                                       idAsignatura=int(controlAsistencia['idAsignatura']),
                                       nombreClase=formatText(controlAsistencia['nombreClase']),
                                       nombreAsignatura=formatText(controlAsistencia['nombreAsignatura']),
                                       nombreProfesor=formatText(controlAsistencia['nombreProfesor']),
                                       fecha=controlAsistencia['fechaHora']
                                     )

    ##############################################
    #   Manejo de imágenes                       #
    ##############################################



    class Imagen(messages.Message):
        name = messages.StringField(1, required=True)
        image  = messages.BytesField(2, required=True)

    @endpoints.method(Imagen, MensajeRespuesta, path='imagenes/subirImagen', http_method='POST', name='imagenes.subirImagen')
    def subirImagen(self, request):

        print 'Nombre recibido:\n'
        print request.name


        # curl -d "nombre=JuanAntonio" -i -X POST -G localhost:8001/_ah/api/helloworld/v1/imagenes/subirImagen

        '''
         (echo -n '{"image": "'; base64 profile.jpg; echo '"}') | curl -H "Content-Type: application/json"  -d @-  localhost:8001/_ah/api/helloworld/v1/imagenes/subirImagen?name=prueba
        '''

        # curl -d "nombre=prueba" -X POST localhost:8001/_ah/api/helloworld/v1/imagenes/subirImagen

        print "\n ##### IMAGEN RECIBIDA EN API ENDPOINTS: #####\n"
        print '\nImagen en CRUDO: \n'
        print str(request.image)

        import binascii
        stringBase64 = binascii.b2a_base64(request.image)
        print '\nImagen pasada a de Base64 a string: \n'
        print stringBase64

        #print request.image.decode(encoding='UTF-8')


        print 'URL \n'
        url = ManejadorImagenes.CreateFile(request.name, request.image)
        print url

        return MensajeRespuesta( message=str(url) )

    @endpoints.method(URL, MensajeRespuesta, path='imagenes/eliminarImagen', http_method='POST', name='imagenes.eliminarImagen')
    def eliminarImagen(self, request):
        '''
        curl -X POST localhost:8001/_ah/api/helloworld/v1/imagenes/eliminarImagen?url=http://localhost:8001/_ah/img/encoded_gs_file:YXBwX2RlZmF1bHRfYnVja2V0L2Zpbm4uanBlZw==
        '''
        print (request.url)
        return MensajeRespuesta( message=ManejadorImagenes.DeleteFile(request.url))


    ##############################################
    #   métodos de CREDENCIALES                  #
    ##############################################

    class Login(messages.Message):
        username = messages.StringField(1, required=True)
        password = messages.StringField(2, required=True)



    @endpoints.method(Login, salidaLogin, path='login/loginUser', http_method='POST', name='login.loginUser' )
    def loginUser(self, request):
        '''
        Comprueba si un usaurio está en elsistema y en caso de estarlo devuelve su ron y su número de identificación.
        curl -d "username=46666&password=46666" -i -X POST -G localhost:8001/_ah/api/helloworld/v1/login/loginUser
        '''

        #Info de seguimiento
        if v:
            print nombreMicroservicio
            print ' Petición POST a login.loginUser'
            print ' Request: \n '+str(request)+'\n'

        #Conformamos la dirección:
        url = "http://%s/" % modules.get_hostname(module=sbd)
        #Añadimos el metodo al que queremos conectarnos.
        url+="comprobarAccesoUsuario"


        #Extraemos lo datos de la petición al endpoints y empaquetamos un dict.
        datos = {
          "username": formatTextInput(request.username),
          "password": formatTextInput(request.password),
        }

        #Petición al microservicio:
        result = urlfetch.fetch(url=url, payload=urllib.urlencode(datos), method=urlfetch.POST)

        json = jsonpickle.decode(result.content)

        if json=='Usuario no encontrado':
            raise endpoints.NotFoundException('Usuario no encontrado')
        else:
            mensajeSalida=salidaLogin(idUser=str(json['idUsuario']), nombre=str(json['nombre']), rol=str(json['rol']))

        #Info de seguimiento
        if v:
            print nombreMicroservicio
            print ' Return: '+str(mensajeSalida)+'\n'


        return mensajeSalida



APPLICATION = endpoints.api_server([HelloWorldApi])
