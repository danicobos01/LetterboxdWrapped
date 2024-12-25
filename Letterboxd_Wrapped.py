import streamlit as st
import pandas as pd
import time
import matplotlib.pyplot as plt
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from bs4 import BeautifulSoup
import threading
from collections import defaultdict
import re
import tmdbsimple as tmdb

tmdb.API_KEY = 'caa88dc630eb5303a1d5b6c73d029ba7'



#@st.experimental_dialog("How to do it?")
#def show_contact_form():



def getCast(url):
    response = requests.get(url)
    final_url = response.url
    soup = BeautifulSoup(response.text, "lxml")


    # directores
    elemento = soup.find_all("a", class_="contributor")
    # dirs = [elem.find("span", class_="prettify").text.strip() for elem in elemento]

    # duracion
    duration = soup.find_all("p", class_="text-link text-footer")
    duration_text = duration[0].get_text(strip=True) if duration else None
    match = re.search(r'(\d+)\s*mins', duration_text) if duration_text else None
    
    if match:
        minutes = match.group(1)
    else:
        minutes = 0 
    

    #valoracion
    valoracion = 0
    try: 
        rating_tag = soup.find_all('meta', {'name': 'twitter:data2'})
        valoracion = float(str(rating_tag[0].get("content")).split()[0]) * 2
    except:
        valoracion = 0

    # popularity
    popularity = -1
    details_section = soup.find("section", class_="section").find("p", class_ = "text-link")
    links = details_section.find("a", text="TMDb")
    tmdb_link = links.get("href")
    tmdb_id = re.search(r'/([a-z]+)/(\d+)/', tmdb_link)
    if tmdb_id.group(1) == "movie":
        id = tmdb_id.group(2)
        a = tmdb.Movies(id).info()
        popularity_tmdb = a['popularity']
        popularity = popularity_tmdb
    else:
        popularity = -1

    # reparto
    crew_section = soup.find("section", class_="section").find("div", {"id": "tab-cast"}).find("div", class_ = "cast-list")
    cast_name = crew_section.find_all("a")
    main_actors = []
    for i in range(len(cast_name)): # Guardamos tres actores principales
        if cast_name[i] != 'Show All…' : main_actors.append((cast_name[i].text, valoracion))
    
    dirs = [elem.find("span", class_="prettify").text.strip() for elem in elemento]
    dirs = [(d, valoracion) for d in dirs]

    return main_actors, dirs, valoracion, final_url, minutes, popularity


def details(role, name, dic):
    if role == "Country" or role == "Countries": dic["paises"].append(name)
    if role == "Primary Language" or role == "Language": dic["idiomas"].append(name)
    if role == "Spoken Languages": dic["idiomas"].append(name)

def procesar_valores(dic_details, url):
    # Obtener los valores de 'paises' e 'idiomas'
    paises = dic_details.get('paises')
    idiomas = dic_details.get('idiomas')
    
    # Convertir a lista si no lo son
    paises = paises if isinstance(paises, list) else [paises]
    idiomas = idiomas if isinstance(idiomas, list) else [idiomas]
    if paises == ['-']: paises = []
    if idiomas == ['-']: idiomas = []
    # print(url, paises, idiomas)
    return paises, idiomas



# funciona
def getDetails(url_1): 
    url = url_1 + 'details/'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "lxml")
    dic_details = {"paises" : [], "idiomas" : []}
    details_section = soup.find("section", class_="section").find("div", {"id": "tab-details"})
    role_names = details_section.find_all("h3")
    # print(role_names)
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

    return procesar_valores(dic_details, url)



# funciona
def getGenres(url_1):
    url = url_1 + "genres/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "lxml")
    g = soup.find("section", class_ = "section").find("div", {"id": "tab-genres"})\
        .find("div", class_="text-sluglist").find_all("a", class_="text-slug")
    genres = []
    for genre in g: 
        genres.append(genre.get_text())
    return genres


def obtener_informacion(letterboxd_url):
    main_actors, directores, valoracion, url, duracion, popularity = getCast(letterboxd_url)
    # print(url)
    paises, idiomas = getDetails(url)
    genres = getGenres(url)
    return main_actors, directores, paises, idiomas, genres, valoracion, letterboxd_url, duracion, popularity


# Función para actualizar los diccionarios
def actualizar_diccionario(diccionario, items):
    for item in items:
        diccionario[item] = diccionario.get(item, 0) + 1

def actualizar_diccionario2(dic, items): 
    for person, valoracion in items:
        dic[person][0] += 1  # Incrementar la cuenta de veces
        dic[person][1] += valoracion  # Sumar la valoración



def actualizar_dic_valoracion(diccionario, uri, valoracion):
    diccionario[uri] = valoracion

# Función para procesar una fila
def procesar_fila(url):
    return url, obtener_informacion(url)


def main_function(dfs):
    max_workers = 10  # Número de hilos simultáneos
    urls = dfs[0]['Letterboxd URI'].dropna().unique()  # Asegurarse de no repetir URLs

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_url = {executor.submit(procesar_fila, url): url for url in urls}
        
        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                _, data = future.result()  # Obtener el resultado del hilo
                if data:
                    actors, directors, countries, languages, genres, valoracion, uri, duracion, popularity = data

                    # Actualizar diccionarios

                    actualizar_diccionario2(st.session_state.directors_dict, directors)
                    actualizar_diccionario2(st.session_state.actors_dict, actors)
                    if countries != []: actualizar_diccionario(st.session_state.countries_dict, countries)
                    if languages != []: actualizar_diccionario(st.session_state.languages_dict, languages)
                    actualizar_diccionario(st.session_state.genres_dict, genres)
                    actualizar_dic_valoracion(st.session_state.films_popularity, uri, popularity)
                    actualizar_dic_valoracion(st.session_state.link_to_avg, uri, valoracion)
                    st.session_state.total_hours += int(duracion)
            except Exception as e:
                print(f"Error procesando {url}: {e}")
                # print(directors, actors, countries, languages, genres, valoracion)    

    st.session_state.directors_dict = {key: (value[0], value[1] / value[0]) for key, value in st.session_state.directors_dict.items()}
    st.session_state.actors_dict = {key: (value[0], value[1] / value[0]) for key, value in st.session_state.actors_dict.items()}
    del st.session_state.actors_dict['Show All…']
    st.session_state.dfs[0]["valoracion_media"] = st.session_state.dfs[0]["Letterboxd URI"].map(st.session_state.link_to_avg)

def transform_df(dfs):  
    df = dfs[0]
    watched_df = dfs[1]

    df['Watched Date'] = pd.to_datetime(df['Watched Date'], errors='coerce')
    df = df[df['Watched Date'].dt.year == 2024]

        # Asegurarnos de que 'Watched Date' está en formato datetime
    df['Watched Date'] = pd.to_datetime(df['Watched Date'], errors='coerce')

    df['Week'] = df['Watched Date'].dt.isocalendar().week
    df['Year_2'] = df['Watched Date'].dt.year

    merged_df = df.merge(watched_df[['Name', 'Year', 'Letterboxd URI']], 
                        on=['Name', 'Year'], 
                        how='left', 
                        suffixes=('', '_new'))
    merged_df['Letterboxd URI'] = merged_df['Letterboxd URI_new'].combine_first(merged_df['Letterboxd URI'])
    merged_df.drop(columns=['Letterboxd URI_new'], inplace=True)

    df = merged_df
    st.session_state.dfs[0] = df


# Título de la aplicación
st.title("Letterboxd Wrapped")



# Subida de múltiples archivos
uploaded_files = st.file_uploader(
    "Selecciona dos archivos para cargar. Tienen que ser diary.csv y watched.csv. Los puedes obtener exportando tus datos desde Letterboxd. Para saber como hacerlo puedes ir a la sección '"'Como Funciona'"'", 
    type=["csv"], 
    accept_multiple_files=True
)

st.session_state.directors_dict = defaultdict(lambda: [0, 0])
st.session_state.actors_dict = defaultdict(lambda: [0, 0])
st.session_state.countries_dict = {}
st.session_state.languages_dict = {}
st.session_state.genres_dict = {}
st.session_state.link_to_avg = {}
st.session_state.films_popularity = {}
st.session_state.total_hours = 0
st.session_state.finished = False

# Verificar si se han subido dos archivos
if uploaded_files:
    if len(uploaded_files) != 2:
        st.warning("Por favor, sube exactamente esos dos archivos.")
    else:

        # Procesar y mostrar cada archivo
        st.session_state.dfs = []
        for file in uploaded_files:
            # st.write(f"Nombre del archivo cargado: {file.name}")
            if file.name.endswith('.csv'):
                if file.name == "diary.csv":
                    df = pd.read_csv(file)
                    st.session_state.dfs.append(df)
                elif file.name == "watched.csv":
                    df1 = pd.read_csv(file)
            else:
                st.error("Formato no soportado.")
                continue
            
        st.session_state.dfs.append(df1)
        st.write("Archivos cargados correctamente")


        st.write("Pulsa a continuación para generar tu resumen del año: ")
        if st.button("Wrapped!"):

            with st.spinner('Se está generando tu resumen (Puede tardar hasta 2 minutos, depende de la cantidad de películas que has visto)'):
                # main_function(dfs)
                transform_df(st.session_state.dfs)
                main_function(st.session_state.dfs)
                st.session_state.finished = True
                time.sleep(2)

            
            st.write("**Ya puedes ver tu resumen!**")


                    
                    
                        
            #progress_text = "Se está generando tu resumen (Puede tardar hasta 2 minutos, depende de la cantidad de películas que has visto)"
            #my_bar = st.progress(0, text=progress_text)

            # Ejecuta la función en segundo plano
            # threading.Thread(target=main_function(dfs), daemon=True).start()

            #for percent_complete in range(100):
               # time.sleep(0.8)
               # my_bar.progress(percent_complete + 1, text=progress_text)
            #time.sleep(1)
            # my_bar.empty()


            # main_function(dfs)
            #st.experimental_rerun()
            # Mostrar el DataFrame
            # st.write("Vista previa del archivo:")
            # st.dataframe(df)
            # st.write("Dimensiones del archivo:", df.shape)