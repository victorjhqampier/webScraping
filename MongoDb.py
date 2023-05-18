from pymongo import MongoClient

class MongoDb(): 
    __cadena_conexion = "mongodb://mongoadmin:getthereveryfast@192.168.3.132:27017"

    def __init__(self):
        self.__client=MongoClient(self.__cadena_conexion)
        self.__db = self.__client["BookRecom"]
        self.__coleccion = self.__db["BooksUnap"]

    def InsertarDatos(self,cDeweyClassi:str,obj_title:dict,obj_casificacion:dict,arrAuthors:list,arrPublisher:list,Copies:list,serial) -> str:
        resultado = self.__coleccion.insert_one({"cDewey":cDeweyClassi,"title":obj_title,"person":arrAuthors,"publisher": arrPublisher,"classification":obj_casificacion,"copy":Copies,"serialTitle":serial})
        return resultado.inserted_id

    # # Consultar documentos
    # documentos = coleccion.find()
    # for documento in documentos:
    #     print(documento)

    # # Cerrar la conexión
    # client.close()