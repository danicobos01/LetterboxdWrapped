import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

# st.set_page_config(layout="wide")

# Título de la aplicación
st.title("TOP ACTORES y DIRECTORES")



def top10actors(dic):
    df = pd.DataFrame(
        [(key, value[0]) for key, value in dic.items()],
        columns=["Actor/Actress", "Films Watched"]
    )
    df = df[df["Actor/Actress"] != 'Show All…']
    df = df.nlargest(10, "Films Watched").reset_index(drop=True)
    return df

def top10directores(dic):
    df = pd.DataFrame(
        [(key, value[0]) for key, value in dic.items()],
        columns=["Director", "Films Watched"]
    )
    df = df.nlargest(10, "Films Watched").reset_index(drop=True)
    return df

def top10actorsValorados(dic):
    df = pd.DataFrame(
        [(key, value[0], value[1]) for key, value in dic.items()],
        columns=["Actor/Actress", "Films watched", "Average Rating"]
    )
    df = df[(df["Films watched"] > 1) & (df["Actor/Actress"] != 'Show All…')]
    df = df.nlargest(10, "Average Rating").reset_index(drop=True)
    return df

def top10directoresValorados(dic):
    df = pd.DataFrame(
        [(key, value[0], value[1]) for key, value in dic.items()],
        columns=["Director", "Films watched", "Average Rating"]
    )
    df = df[df["Films watched"] > 1]
    df = df.nlargest(10, "Average Rating").reset_index(drop=True)
    return df

def app():
    # Acceder a la variable definida en app.py a través de st.session_state
    if 'actors_dict' in st.session_state and st.session_state.finished == True:


        # Crear columnas para dividir el contenido
        col1, col2 = st.columns(2)

        # Mostrar "Top 10 actores más vistos" en la primera columna
        with col1:
            st.write("**Top 10 actores más vistos**")
            st.dataframe(top10actors(st.session_state.actors_dict))
            

        # Mostrar "Top 10 directores más vistos" en la segunda columna
        with col2:
            st.write("**Top 10 directores más vistos**")
            st.dataframe(top10actors(st.session_state.directors_dict))
            
        st.write("**Top 10 actores con mayor valoración media (mínimo dos películas vistas)**")
        st.dataframe(top10actorsValorados(st.session_state.actors_dict))
        st.write("**Top 10 directores con mayor valoración media (mínimo dos películas vistas)**")
        st.dataframe(top10actorsValorados(st.session_state.directors_dict))
    else:
        st.write("Por favor, introduce primero los archivos necesarios")


app()