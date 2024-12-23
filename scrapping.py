import requests
from bs4 import BeautifulSoup
import cchardet as chardet
from concurrent.futures import ThreadPoolExecutor
import json
import re
import tmdbsimple as tmdb

user = 'danicpppp'
prefix = "https://letterboxd.com"
numpag = 1
tmdb.API_KEY = 'caa88dc630eb5303a1d5b6c73d029ba7'

# Inicializar una lista vacia para almacenar informacion sobre las peliculas
movies = []

# Funcion que traduce un string de estrellas en una valoracion numerica
def starsToNumber(valoracion):
    cont = 0
    for i in range(0, len(valoracion)):
        if valoracion[i] == '★': cont += 2
        elif valoracion[i] == '½': cont += 1
    return cont

# Funcion auxiliar que comprueba el rol de alguien del rodaje y lo introduce en un diccionario
def roles(role, name, dic):
    if role == "Directors" or role == "Director": dic["Direccion"].append(name)
    if role == "Producers" or role == "Producer": dic["Produccion"].append(name)
    if role == "Writers" or role == "Writer": dic["Guion"].append(name)
    if role == "Editors" or role == "Editor": dic["Edicion"].append(name)
    if role == "Cinematography" or role == "Cinematographers": dic["Cinematografia"].append(name)

def details(role, name, dic):
    if role == "Studios" or role == "Studio": dic["Productoras"].append(name)
    if role == "Country" or role == "Countries": dic["Pais principal"].append(name)
    if role == "Original Language" or role == "Language": dic["Idioma principal"].append(name)



# Devuelve el año de estreno de una pelicula
def getYear(link):
    url = prefix + "/film/" + link
    print(url)
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "lxml")
    y = soup.find("div", class_ = "releaseyear")
    y = y.find("a")
    year = y.get_text()
    return year

# Devuelve generos de una pelicula
def getGenres(link): 
    url = prefix + "/film/" + link + "/genres"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "lxml")
    g = soup.find("section", class_ = "section").find("div", {"id": "tab-genres"})\
        .find("div", class_="text-sluglist").find_all("a", class_="text-slug")
    genres = []
    for genre in g: 
        genres.append(genre.get_text())
    return genres


def getCast(link):
    url = prefix + "/film/" + link
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "lxml")
    crew_section = soup.find("section", class_="section").find("div", {"id": "tab-cast"}).find("div", class_ = "cast-list")
    cast_name = crew_section.find_all("a")
    main_actors = []
    for i in range(3): # Guardamos tres actores principales
        if i < len(cast_name) and cast_name[i] is not None: main_actors.append(cast_name[i].text) # en caso de que no haya tres actores
        else: main_actors.append("-")
    return main_actors

# Devuelve parte del equipo de rodaje de una pelicula
def getCrew(link):
    dic_crew = {"Direccion" : [], "Produccion" : [], "Guion" : [], "Edicion" : [], "Cinematografia" : []}
    url = prefix + "/film/" + link + "/crew"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "lxml")
    crew_section = soup.find("section", class_="section").find("div", {"id": "tab-crew"})
    role_names = crew_section.find_all("h3")
    for role_name in role_names:
        if(role_name.find_next("div").get("class") == "tabbed-content-block"): break
        names_section = role_name.find_next("div", class_="text-sluglist")
        if names_section:
            names_exact = names_section.find_all("a")
            for name in names_exact:
                roles(role_name.text.splitlines()[1], name.text, dic_crew)

    for clave, valores in dic_crew.items():
        if len(valores) == 1: dic_crew[clave] = valores[0]
        if len(valores) == 0: dic_crew[clave] = "-"
    return dic_crew

def getDetails(link):
    dic_details = {"Productoras" : [], "Pais principal" : [], "Idioma principal" : []}
    url = prefix + "/film/" + link + "/details"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "lxml")
    details_section = soup.find("section", class_="section").find("div", {"id": "tab-details"})
    role_names = details_section.find_all("h3")
    for role_name in role_names:
        if(role_name.find_next("div").get("class") == "tabbed-content-block"): break
        names_section = role_name.find_next("div", class_="text-sluglist")
        if names_section:
            names_exact = names_section.find_all("a")
            for name in names_exact:
                details(role_name.text, name.text, dic_details)

    for clave, valores in dic_details.items():
        if len(valores) == 1: dic_details[clave] = valores[0]
        if len(valores) == 0: dic_details[clave] = "-"
    return dic_details

def getTmdb(link):
    url = prefix + "/film/" + link
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "lxml")
    details_section = soup.find("section", class_="section").find("p", class_ = "text-link")
    duracion = re.search(r'\d+',details_section.text).group()
    links = details_section.find("a", text="TMDb")
    tmdb_link = links.get("href")
    tmdb_id = re.search(r'/([a-z]+)/(\d+)/', tmdb_link)
    if tmdb_id.group(1) == "movie":
        id = tmdb_id.group(2)
        a = tmdb.Movies(id).info()
        budget = a['budget']
        ingresos = a['revenue']
        valoracion_tmdb = a['vote_average']
        popularity_tmdb = a['popularity']
        movie = True
        return [duracion, budget, ingresos, valoracion_tmdb, popularity_tmdb, movie]
    else:
        return [duracion, "-", "-", "-", "-", False]



def getAverageRating(link):
    url = prefix + "/film/" + link
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "lxml")

    #with open("response.txt", "w", encoding="utf-8") as archivo:
       # archivo.write(response.text)

    rating_tag = soup.find_all('meta', {'name': 'twitter:data2'})
    valoracion = float(str(rating_tag[0].get("content")).split()[0]) * 2
    return valoracion

# Devuelve toda la información de la pelicula
def getInfoMovie(link):
    y = getYear(link)
    g = getGenres(link)
    crew = getCrew(link)
    cast = getCast(link)
    details = getDetails(link)
    infoTmdb = getTmdb(link)
    avg = getAverageRating(link)
    dic = {"average_rating": avg, "year_release" : y, "genres" : g, "main_actor 1": cast[0], "main_actor 2": cast[1], "main_actor 3": cast[2],
           "runtime" : infoTmdb[0], "budget" : infoTmdb[1], "ingresos" : infoTmdb[2], "valoracion_tmdb" : infoTmdb[3], 
           "popularity" : infoTmdb[4], "is_movie": infoTmdb[5]}
    print(dic)
    return {**dic, **crew, **details}

# Para cada entrada de pelicula extrae toda la informacion importante
def funcion(entry):
    # print(entry.prettify())
    info = entry.find("div", class_="really-lazy-load") 
    data_film_slug = info.get("data-film-slug")
    print(data_film_slug)
    # input(data_film_slug)
    dic = getInfoMovie(data_film_slug) # data-film-slug contiene el link
    print(data_film_slug)
    title = entry.find("img")
    print(title)
    #print(title["alt"])
    rating = entry.find("span", class_="rating")
    if rating is not None: 
        valoracion = starsToNumber(rating.get_text())
    else: 
        valoracion = 0

    like = entry.find("span", class_ = "like")
    if like is not None: heart = True
    else: heart = False

    # Agregar un diccionario con la informacion de la pelicula a la lista
    dicMovies = {"title": title["alt"], "rating": valoracion, "has_like": heart, "film_id": str(info['data-film-slug'])}
    print(dicMovies)
    dicMovies.update(dic)
    movies.append(dicMovies)
    # print(dicMovies)



def main_function(n): 
    url = f"{prefix}/{user}/films/page/{n}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "lxml")
    movie_entries = soup.find_all("li", class_="poster-container")
    with  ThreadPoolExecutor(max_workers=len(movie_entries)) as executor:
        for entry in movie_entries:
            executor.submit(funcion, entry)

next = True
while next: 
    url = f"{prefix}/{user}/films/page/{numpag}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "lxml")
    if soup.find("a", class_="next") is None: 
        next = False
    else: 
        numpag += 1
        print("pagina ", numpag, " completada")

num_pages = [i for i in range(1, numpag)]

with ThreadPoolExecutor(max_workers=len(num_pages)) as executor:
    for n in num_pages:  
        executor.submit(main_function, n)


"""
next = True
while next:
    url = f"{prefix}/{user}/films/page/{numpag}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "lxml")
    movie_entries = soup.find_all("li", class_="poster-container")
    print(len(movie_entries))
    with  ThreadPoolExecutor(max_workers=len(movie_entries)) as executor:
        for entry in movie_entries:
            executor.submit(funcion, entry)
    
    if soup.find("a", class_="next") is None: 
        next = False
    else: 
        numpag += 1
        print("pagina ", numpag, " completada")

"""

# Imprimir en un json todas las peliculas del usuario 
with open(fr'C:\Users\danic\Python Projects\RecomendadorLetterboxd\pelis_{user}_prueba2.json', 'w') as j:
        json.dump(movies, j, indent=2, separators=(",", ":"))


# Exportarlo a csv tambien para que sea compatible con el dataset extraido de kaggle

