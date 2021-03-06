# -*- coding: utf-8 -*-
"""
asfdljaslkhfadsjkhfa

"""

from google.appengine.ext.db import Key
from EstructurasNDB import *
import datetime

#Para activar/desactivar el modo verbose para muestra de mensajes.
v = 1
libName='\n ## Gestor NDB ##'


def parseBoolean(cadena):
    """This function does something.

    Args:
       name (str):  The name to use.

    Kwargs:
       state (bool): Current state to be in.

    Returns:
       int.  The return code::

          0 -- Success!
          1 -- No good.
          2 -- Try again.

    Raises:
       AttributeError, KeyError

    A really great idea.  A way you might use me is

    >>> print public_fn_with_googley_docstring(name='foo', state=None)
    0

    BTW, this always returns 0.  **NEVER** use with :class:`MyPublicClass`.
    """
    if cadena=='True' or cadena== 1 or cadena == '1' :
        return True
    if cadena=='False' or cadena == 0 or cadena == '0' :
        return False


def boolToInt(boolean):
    if boolean == True:
        return 1
    if boolean == False:
        return 0

class RCA:

    def __init__(self):
        key = ""
        fecha = ""
        idClase = ""
        nombreClase = ""
        idAsignatura = ""
        nombreAsignatura = ""
        idProfesor = ""
        nombreProfesor = ""

class Gestor:

    @classmethod
    def insertar_prueba(self):

        print '\n\n Insertando prueba \n\n'

        prueba = Prueba()
        prueba.texto='Hola'

        #Cuando insertamos la entidad en el datastore nos devuelve la clave con la que puede ser depués recuperada
        prueba_key = prueba.put()

        pruebaDev = prueba_key.get()
        print pruebaDev




    @classmethod
    def obtenerALLCA(self):
        '''
        Devuelve una lista completa con todos los controles de asistencia.
        '''
        listaCA = []
        listaCA = ControlAsistencia.devolver_todo().fetch(100000)

        return listaCA

    @classmethod
    def obtenerControlAsistencia(self, id):
        '''
        Devuelve un control de asistencia completo realizado, con la lista de todos los alumnos, y los datos de ese
        control en concreto.
        '''
        #Una vez obtenido la clave del resumen vamos a obtener todas los controles que se realizaron en
        #ese control y para ello lo primero que tenemos que recuperar es la lista de las claves de los controles
        #refiriéndonos con control al control que se hace de un estudiante individual.

        print 'KEY'
        print id
        #Convertimos el id recibido en una clave procesable por ndb
        key = ndb.Key('ResumenControlAsistencia', long(id));
        print key

        #Realizamos la consulta
        query = ResumenControlAsistencia.query(ResumenControlAsistencia.key == key)

        print '\n PROCESO OBTENCIÓN CONTROL ASISTENCIA '

        #Comprobamos cuantos resultados hemos obtenido.
        #https://cloud.google.com/appengine/docs/python/ndb/queryclass#Query_count
        #Si se ha encontrado un control con ese id
        if (query.count()==1):
            #Rescatamos el resumen
            resumen = query.get()

            print 'RESUMEN'
            print str(resumen)

            #Una vez recuperado el resumen tendremos que componer una lista donde cada elemento será el control de un
            #estudiante en concreto al que llegaremos gracias a que resumen tiene sus claves almacenadas.

            #Rescatamos la lista de Controles de Asistencia
            listaKeysMCA=resumen.lista_idCA


            #Vamos a usar algo parecido a los struct de C para estructurar un objeto que devolver.
            #http://docs.python.org.ar/tutorial/2/classes.html

            class Control:
                pass
            class CA:
                pass

            listaControles = []

            #Recorremos la lista (que contiene las claves de los mcontroles) para rellenar las litas de controles
            for key in listaKeysMCA:
                query = ControlAsistencia.query(ControlAsistencia.key==key)
                #mc=mcontrol=microcontrol
                mc=query.get()
                print 'microcontrol leido'
                print mc
                #Creamos un registro de Control vacío
                control = Control()
                #Llenamos los campos del registro con lo que nos interesa
                control.asistencia=boolToInt(mc.asistencia)
                control.retraso=mc.retraso
                control.retrasoJustificado=mc.retraso_justificado
                control.uniforme=mc.uniforme
                control.idAlumno=mc.id_alumno

                #Además tb queremos añadir su nombre para que se vea en la interfaz
                query = Alumno.query(Alumno.idAlumno==int(mc.id_alumno))
                alumno = query.get()
                control.nombreAlumno=alumno.nombreAlumno

                listaControles.append(control)
                print 'Objeto control creado'
                print control.__dict__


            #Ahora creamos el objeto ControlAsistencia añadiendo los datos  comunes a todos los mcontrolesAsistencia
            ca = CA()
            #La lista
            ca.controles=listaControles

            #Los datos comunes a todos que obtnemos del primer elemento (podría ser de cualquiera)
            cualquiera = ControlAsistencia.query(ControlAsistencia.key==listaKeysMCA[0]).get()
            ca.idProfesor = cualquiera.id_profesor
            ca.idClase = cualquiera.id_clase
            ca.idAsignatura = cualquiera.id_asignatura

            #Además queremos añadir a la parte común el nombre de la clase, de la asignatura y del profesor,
            #ya que son comunes y queremos que se muestren en la UI. Estos datos los tiene la NDB en tablas separadas,
            #accedemos a los datos y los añadimos.

            #Clase
            query = Clase.query(Clase.idClase==int(cualquiera.id_clase))
            clase = query.get()
            ca.nombreClase=clase.nombreClase

            #Asignatura
            query = Asignatura.query(Asignatura.idAsignatura==int(cualquiera.id_asignatura))
            asignatura = query.get()
            ca.nombreAsignatura=asignatura.nombreAsignatura

            #Profesor
            query = Profesor.query(Profesor.idProfesor==int(cualquiera.id_profesor))
            profesor = query.get()
            ca.nombreProfesor=profesor.nombreProfesor

            #Devolvemos la fecha en texto plano ya formateado
            ca.fechaHora = datetime.datetime.strftime(cualquiera.fecha_hora, "%d-%m-%Y %H:%M")

            print 'Finally'
            print ca.__dict__

            #Devolvemos el control de asistencia construido
            return ca

        else:
            return 'Error not found.'


    @classmethod
    def obtenerResumenesControlAsistencia(self, idProfesor=None, idASignatura=None, idClase=None, fechaHora=None):
        """
        Con todos los parámetros a None esta función puede ser llamada con desde 0 a 4 parámetros.
        Debe devolver también nombres (DEBE DEVOLVER UN RCA_complejo)

        Tipo de resumen a devolver.
        Lo que tiene que devolver el gateway:
        class ResumenControlAsistencia(messages.Message):
            key = messages.StringField(1, required=True)
            fecha = messages.StringField(2)
            idClase = messages.StringField(3)
            nombreClase = messages.StringField(4)
            idAsignatura = messages.StringField(5)
            nombreAsignatura = messages.StringField(6)
            idProfesor = messages.StringField(7)
            nombreProfesor = messages.StringField(8)

        class ResumenControlAsistencia(ndb.Model):

            lista_idCA = ndb.KeyProperty(repeated=True) # La propiedad repeated hace que el campo sea una lista y pueda tomar varios valores, en lugar de solo unof
            fecha_hora = ndb.DateTimeProperty()
            id_profesor = ndb.IntegerProperty()
            id_clase = ndb.IntegerProperty()
            id_asignatura = ndb.IntegerProperty()

        Los datos que se tienen en la NDB siguen el anterior esquema, pero el APIG necesit más datos. Por ello
        crearemos un tipo de objeto nuevo que contenga todo lo que necesita y por el que no haya que modificar
        la definiión de la BD NDB.

        """
        if v:
            print libName
            print " Llamada a NDBlib.gestor.obtenerResumenesControlAsistencia() "
            print locals()

        #Creamos una lista de resúmenes que vamos a devoler.
        resumenes = []

        if (idProfesor!=None):
            #Formamos la query
            query = ResumenControlAsistencia.query(ResumenControlAsistencia.id_profesor == int(idProfesor))
            #Ejecutamos la query en NDB, y por cada elemento creamos un objeto RCA y le volcamos los datos.
            for a in query:
                #Creamos el objeto
                rca = RCA()
                #Guardamos el id de la clave
                rca.key = a.key.id()
                #Convertimos la fecha en algo legible con el formato que queramos.
                rca.fecha = datetime.datetime.strftime(a.fecha_hora, "%d-%m-%Y %H:%M")
                rca.idClase = a.id_clase
                rca.idAsignatura = a.id_asignatura
                rca.idProfesor = a.id_profesor

                #Ahora tenemos que añadir los nombre de la clase, asignatura y profesor.

                #Clase
                query = Clase.query(Clase.idClase==int(1))
                clase = query.get()
                rca.nombreClase=clase.nombreClase

                #Asignatura
                query = Asignatura.query(Asignatura.idAsignatura==int(1))
                asignatura = query.get()
                rca.nombreAsignatura=asignatura.nombreAsignatura

                #Profesor
                query = Profesor.query(Profesor.idProfesor==int(1))
                profesor = query.get()
                rca.nombreProfesor=profesor.nombreProfesor

                #Con esto queda el objeto preparado para devolverlo al APIG

                #print 'RCA parseado'
                # Para ver todos los atributos de un objeto con sus valores podemos implementar la función __str__ o usar __dict__
                # print rca.__dict__

                #Lo añadimos a la lista
                resumenes.append(rca)


        if v:
            print libName
            print " Return obtenerResumenesControlAsistencia "
            for r in resumenes:
                #print 'KEY'
                #print r.key
                print r.__dict__

        #Devolvemos la lista, tenga 0, 1 o n elementos.
        return resumenes


    ###
    #Métodos de la inserccion de un control de asistencia completo.
    ###

    @classmethod
    def insertarConjuntoControlAsistencia(self, listaAsistencias):
        '''
        Inserta en el sistema un control de asistencia (conjunto de ellos) compuesto por al menos un
        control de asistencia de un estudiante(los llamamos igual).
        Recibimos una lista con los controles.
        '''
        if v:
            print libName
            print " Llamada a insertarConjuntoControlAsistencia "
            print locals()

        #Creamos una lista donde guardaremos las keys que la base de datos nos devuelva al guardar los controles.
        keys = []

        #Establecemos el datetime para usar el mismo en todas las asistencias al guardarlas, cogiéndolo del sistema.
        fechahora = datetime.datetime.now()
        if v:
            print 'Datetime usado:'
            print fechahora

        #Recorremos todos los elementos de la lista pasada
        for asistencia in listaAsistencias:
            #Insertarmos una asistencia en el sistema con una función y guardamos su salida en la lista de keys.
            keys.append(Gestor.insertarControlAsistencia(asistencia, fechahora))

        '''
        Una vez que se han introducido las asistencias en la tabla ControlAsistencia tenemos que crear un resumen
        en la tabla ResumenControlAsistencia y para eso usamos el método insertarResumenControlAsistencia. Para extraer
        los tres últimos parámetros usamos el primer control pasado en la lista.
        '''

        keyResumen=Gestor.insertarResumenControlAsistencia(keys, fechahora, (listaAsistencias[0])['idProfesor'],
                                                                 (listaAsistencias[0])['idAsignatura'],
                                                                 (listaAsistencias[0])['idClase']
                                               )

        return 'OK'

    @classmethod
    def insertarControlAsistencia(self, control, datetime):
        '''
        Inserta una asistencia en la tabla ControlAsistencia del datastore.
        Devuelve la clave de objeto introducido.
        '''

        #Info de seguimiento
        if v:
            print libName
            print " Llamada a insertarControlAsistencia con params: "
            print locals()
            print '\n'

        #Se crea una instancia del modelo
        nuevoCA = ControlAsistencia()

        #Se rellena de datos, ajustándolos a los que esperamos.
        nuevoCA.fecha_hora=datetime #Usamos directamente la fecha y hora que nos pasan.
        nuevoCA.asistencia=parseBoolean(control['asistencia'])
        nuevoCA.retraso=int(control['retraso'])
        #nuevoCA.retraso_tiempo=int(control['retraso_tiempo'])
        nuevoCA.retraso_justificado=parseBoolean(control['retrasoJustificado'])
        nuevoCA.uniforme=parseBoolean(control['uniforme'])
        nuevoCA.id_alumno=int(control['idAlumno'])
        nuevoCA.id_profesor=int(control['idProfesor'])
        nuevoCA.id_clase=int(control['idClase'])
        nuevoCA.id_asignatura=int(control['idAsignatura'])

        #Se guarda en el data store
        nuevoCA_clave = nuevoCA.put()

        #Info de seguimiento
        if v:
            print libName
            print " Return de insertarControlAsistencia: "+str(nuevoCA_clave)+'\n'

        return nuevoCA_clave

    @classmethod
    def insertarResumenControlAsistencia(self, listaIdCA, fechaHora,idProfesor,idASignatura,idClase):
        #Info de seguimiento
        if v:
            print libName
            print " Llamada a insertarResumenControlAsistencia con params: "
            print locals()
            print '\n'

        #Se crea una instancia del modelo
        nuevoRCA = ResumenControlAsistencia()

        #Se rellena de datos, ajustándolos a los que esperamos.
        nuevoRCA.lista_idCA=listaIdCA
        nuevoRCA.fecha_hora=fechaHora
        nuevoRCA.id_profesor=idProfesor
        nuevoRCA.id_clase=idClase
        nuevoRCA.id_asignatura=idASignatura


        #Se guarda en el data store
        nuevoRCA_clave = nuevoRCA.put()

        #Info de seguimiento
        if v:
            print libName
            print " Return de insertarResumenControlAsistencia: "+str(nuevoRCA_clave)+'\n'

        return nuevoRCA_clave


    @classmethod
    def insertarAlumno(self, idAlumno, nombreAlumno):

        #Info de seguimiento
        if v:
            print libName
            print " Llamada a insertarAlumno con params: "
            print locals()
            print '\n'

        alumno = Alumno()
        alumno.idAlumno=int(idAlumno)
        alumno.nombreAlumno=nombreAlumno

        salida = {}

        try:
            nuevoAlumnoClave = alumno.put()
            salida['status']='OK'
        except ValueError:
            salida['status']='FAIL'

        #Info de seguimiento
        if v:
            print libName
            print " Return de insertarAlumno: "+str(nuevoAlumnoClave)+'\n'

        salida['id']=nuevoAlumnoClave

        return salida


    @classmethod
    def insertarProfesor(self, idProfesor, nombreProfesor):

        #Info de seguimiento
        if v:
            print libName
            print " Llamada a insertarProfesor con params: "
            print locals()
            print '\n'

        profesor = Profesor()
        profesor.idProfesor=int(idProfesor)
        profesor.nombreProfesor=nombreProfesor

        salida = {}

        try:
            nuevoProfesorClave = profesor.put()
            salida['status']='OK'
        except ValueError:
            salida['status']='FAIL'

        #Info de seguimiento
        if v:
            print libName
            print " Return de insertarProfesor: "+str(nuevoProfesorClave)+'\n'

        salida['id']=nuevoProfesorClave

        return salida

    @classmethod
    def insertarClase(self, idClase, nombreClase):

        #Info de seguimiento
        if v:
            print libName
            print " Llamada a insertarClase con params: "
            print locals()
            print '\n'

        clase = Clase()
        clase.idClase=int(idClase)
        clase.nombreClase=nombreClase

        salida = {}

        try:
            nuevaClaseClave = clase.put()
            salida['status']='OK'
        except ValueError:
            salida['status']='FAIL'

        #Info de seguimiento
        if v:
            print libName
            print " Return de insertarClase: "+str(nuevaClaseClave)+'\n'

        salida['id']=nuevaClaseClave

        return salida


    @classmethod
    def insertarAsignatura(self, idAsignatura, nombreAsignatura):

        #Info de seguimiento
        if v:
            print libName
            print " Llamada a insertarAsignatura con params: "
            print locals()
            print '\n'

        asignatura = Asignatura()
        asignatura.idAsignatura=int(idAsignatura)
        asignatura.nombreAsignatura=nombreAsignatura


        salida = {}

        try:
            nuevaAsignaturaClave = asignatura.put()
            salida['status']='OK'
        except ValueError:
            salida['status']='FAIL'


        #Info de seguimiento
        if v:
            print libName
            print " Return de insertarAsignatura: "+str(nuevaAsignaturaClave)+'\n'

        salida['id']=nuevaAsignaturaClave

        return salida



    @classmethod
    def obtenerNombreProfesores(idProfesor):
        pass

    @classmethod
    def obtenerNombreClases(idClase):
        pass

    @classmethod
    def obtenerNombreAsignaturas(idAsignatura):
        pass
