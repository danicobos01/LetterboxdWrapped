import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import plotly.express as px

st.title("TOP DETALLES")


def mapamundi(dic):
    # Convertir el diccionario en un DataFrame
    df = pd.DataFrame(list(dic.items()), columns=["Country", "Films watched"])

    # Crear el mapa con Plotly
    fig = px.choropleth(
        df, 
        locations="Country",  # Nombre de los países
        locationmode="country names",  # Usar nombres de países
        color="Films watched",  # Valor para determinar el color
        hover_name="Country",  # Mostrar el nombre del país al pasar el ratón
        color_continuous_scale=["lightgreen", "green"],  # Escala de colores
        title="Mapa de los países de películas que has visto"
    )

    # Ajustar para mostrar un solo color para países no destacados
    fig.update_traces(
        colorbar=dict(title="Resaltado"),
        showscale=False  # Opcional: Oculta la barra de escala si no es necesaria
    )

    # Mostrar el mapa en Streamlit
    st.plotly_chart(fig)

def top5Generos(dic):
    df = pd.DataFrame(list(dic.items()), columns=["Genre", "Films Watched"])
    df["Films Watched"] = pd.to_numeric(df["Films Watched"], errors='coerce')
    df = df.dropna(subset=["Films Watched"])
    df = df.nlargest(5, "Films Watched").reset_index(drop=True)
    return df

def top5Idiomas(dic):
    df = pd.DataFrame(list(dic.items()), columns=["Language", "Films Watched"])
    df = df.nlargest(5, "Films Watched").reset_index(drop=True)
    return df

def convert_to_hours_minutes(total_minutes):
    hours = total_minutes // 60  # Dividir para obtener las horas
    minutes = total_minutes % 60  # Obtener el resto para los minutos
    return hours, minutes

def convert_to_days_hours(total_minutes):
    days = total_minutes // 1440  # Dividir para obtener los días (1440 minutos en un día)
    hours = (total_minutes % 1440) // 60  # Obtener el resto para los minutos y luego dividir entre 60 para obtener las horas
    return days, hours

def app():
    # Acceder a la variable definida en app.py a través de st.session_state
    if 'countries_dict' in st.session_state and st.session_state.finished == True:
        with st.spinner('Está cargando el mapamundi (no tardará más de unos segundos)'):
            mapamundi(st.session_state.countries_dict)
        
        col1, col2 = st.columns(2)

        # Mostrar "Top 10 actores más vistos" en la primera columna
        with col1:
            st.write("**Top 5 géneros más vistos**")
            st.dataframe(top5Generos(st.session_state.genres_dict))
        
        with col2:
            st.write("**Top 5 idiomas más vistos**")
            st.dataframe(top5Generos(st.session_state.languages_dict))

        st.write("**Este año has estado:**")
        st.write(f" - **{int(st.session_state.total_hours)} minutos** viendo películas")
        hours, minutes = convert_to_hours_minutes(int(st.session_state.total_hours))
        st.write(f" - **{hours} horas  y {minutes} minutos** viendo películas!")
        days, hours2 = convert_to_days_hours(int(st.session_state.total_hours))
        st.write(f" - **{days} dias y {hours2} horas** viendo películas!!")







    else:
        st.write("Por favor, introduce primero los archivos necesarios")


app()
