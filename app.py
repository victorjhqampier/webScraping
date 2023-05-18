import requests
from bs4 import BeautifulSoup

from MongoDb import MongoDb

url = "https://biblioteca.unap.edu.pe/opac_css/"
newPage = "index.php?lvl=section_see&location=21&id=41"

nPage = 15
nNoProcess = 0
while (nPage > 0):
    res = requests.get(url + newPage)
    contenido_html = res.text

    soup = BeautifulSoup(contenido_html, "html.parser")
    notice_child = soup.select(".notice-child")

    for child in notice_child:
        try:
            if child.select_one(".public_indexint a") is None or child.select_one(".public_indexint a").text.strip() =="":
                nNoProcess = nNoProcess + 1        
                continue
            cDeweyClassi = child.select_one(".public_indexint a").text.strip()
            cTtile = child.select_one(".public_title").text
            cImage = child.select_one(".vignetteimg")["vigurl"] #pageDriver.FindElement(By.CssSelector(".vignetteimg")).GetAttribute("src") ?? "";
            obj_title = {
                "cTitle": cTtile.split(":")[0].strip() if ": " in cTtile else cTtile,
                "cSubtitle": cTtile.split(":")[1].strip() if ": " in cTtile else "",
                "cIsbn": child.select_one(".public_code").text if child.select_one(".public_code") is not None else "",
                "cEdition": child.select_one(".public_mention").text if child.select_one(".public_mention") is not None else "",
                "nReleased": int(child.select_one(".public_year").text) if child.select_one(".public_mention") is not None else 0,
                "cContent": child.select_one(".public_contenu").text,
                "cNotes": child.select_one(".public_ngen").text if child.select_one(".public_ngen") is not None else "",
                "cTopics": child.select_one(".public_indexint span").text if child.select_one(".public_indexint span") is not None else "",
                "cType": "Libro",
                "cImage": cImage if cImage.startswith("http") and len(cImage) < 380 else ""
            }

            obj_casificacion = {
                "cCode": child.select_one(".public_indexint a").text,
                "cDescription": child.select_one(".public_indexint span").text if child.select_one(".public_indexint span") is not None else ""
            }

            arrAuthors = []
            uniqueAuthors = set()
            for item in child.select_one(".public_auteurs").text.split(";"):
                arrAuthor = item.split(",")
                name = arrAuthor[1].strip() if len(arrAuthor) > 2 else ""
                author = {
                    "cName": name.split("(")[0].strip() if "(" in name else name,
                    "cRole": arrAuthor[-1].strip(),
                    "cSurname": arrAuthor[0].strip(),
                    "cPlace": "(" + name.split("(")[1].strip() if "(" in name else ""
                }
                authorTuple = tuple(author.items())  # Convertir el diccionario en una tupla
                if authorTuple not in uniqueAuthors:
                    uniqueAuthors.add(authorTuple)
                    arrAuthors.append(author)
            
            arrPublisher = []
            for item in child.select_one(".public_ed1 a").text.split(";"):
                arrEdi = item.split(":")
                arrPublisher.append({
                    "cName": arrEdi[1].strip() if len(arrEdi) > 1 else arrEdi[0],
                    "cPlace": arrEdi[0].strip() if len(arrEdi) > 1 else ""
                })
            
            Copies = []
            Copies.append({
                "cNotation": child.select(".expl_cote")[0].text,
                "cLibrary": "UNA Puno, " + child.select(".location_libelle")[0].text,
                "cLink": "https://biblioteca.unap.edu.pe/opac_css"
            })
            serial = None
            # if(child.select(".tr_serie td") is not None):
            for item in child.select(".tr_serie td"):
                if item.text.startswith("Título"):
                    continue
                arrCode = item.text.split(",")
                Serial = {
                    "cNumber": arrCode[1] if len(arrCode) > 1 else "",
                    "cTitle": arrCode[0]
                }
            obj_mongo = MongoDb()
            print(obj_mongo.InsertarDatos(cDeweyClassi,obj_title,obj_casificacion,arrAuthors,arrPublisher,Copies,serial))
        except Exception as ex:
            print("Error : " + str(ex))
        
    if(nNoProcess >= 13):
        nPage = nPage + 1
        nNoProcess = 0
    
    nPage = nPage - 1   
    newPage = soup.select_one("a.navbar_next")["href"][2:]
    print("Pagina : " + str(nPage), "\n")