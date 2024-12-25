import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import altair as alt


# Título de la aplicación
st.title("TOP PELICULAS")



def getTop10(df):
    df_res = df.nlargest(10, 'valoracion_media')[['Name','Year', 'valoracion_media', 'Rating', 'Letterboxd URI']].reset_index(drop=True)
    df_res = df_res.rename(columns={'valoracion_media': 'Average Rating', 'Letterboxd URI' : 'Letterboxd URL'})
    df_res['Rating'] = df_res['Rating'].fillna(0)
    df_res['Year'] = df_res['Year'].astype(int).astype(str)
    df_res['Year'] = df_res['Year'].apply(lambda x: str(int(float(x))) if isinstance(x, (int, float)) else str(x))
    st.write("**Las 10 películas con mayor valoración media que has visto**")
    st.dataframe(df_res)


def getWorst5(df):
    df_res = (
        df[df['valoracion_media'] > 0]  # Filtrar las filas donde 'valoracion_media' es mayor que 0
        .nsmallest(5, 'valoracion_media')[['Name', 'Year', 'valoracion_media', 'Rating', 'Letterboxd URI']].reset_index(drop=True)
    )
    df_res['Rating'] = df_res['Rating'].fillna(0)
    df_res = df_res.rename(columns={'valoracion_media': 'Average Rating', 'Letterboxd URI' : 'Letterboxd URL'})
    df_res['Year'] = df_res['Year'].astype(int).astype(str)
    st.write("**Las 5 películas con peor valoración que has visto**")
    st.dataframe(df_res)

def getDecadas(df):
    # Crear la columna de 'decada'
    df['decada'] = (df['Year'] // 10) * 10
    
    # Filtrar las décadas con más de 1 película
    decadas_filtradas = df.groupby('decada').filter(lambda x: len(x) > 1)
    
    # Obtener la década mejor valorada
    decada_mejor_valorada = (
        decadas_filtradas.groupby('decada')['Rating']  # Agrupamos por década y calculamos media de 'rating'
        .mean()
        .idxmax()  # Obtenemos la década con mayor media
    )
    st.write("\n")
    st.write(f"**La década con mayor valoración media es: {decada_mejor_valorada}**")
    
    # Calcular la media por década
    media_por_decada = decadas_filtradas.groupby('decada')['Rating'].mean().reset_index()
    
    # Crear gráfico de barras con Altair
    chart = alt.Chart(media_por_decada).mark_bar(color='green').encode(
        x=alt.X('decada:O', title='Década'),
        y=alt.Y('Rating:Q', title='Valoración Media', scale=alt.Scale(domain=[0, 5])),  # Escala Y ajustada
        tooltip=['decada', 'Rating']
    ).properties(
        title='Valoración Media por Década',
        width=600,
        height=400
    )
    
    # Añadir las etiquetas de los valores encima de las barras con dos decimales
    text = chart.mark_text(
        align='center',
        baseline='middle',
        dy=-10,  # Ajustar la posición de las etiquetas
        fontSize=12,
        color='black'
    ).encode(
        text=alt.Text('Rating:Q', format='.2f')  # Limitar a dos decimales
    )
    
    # Combinar el gráfico de barras con las etiquetas
    final_chart = chart + text

    # Mostrar el gráfico en Streamlit
    st.altair_chart(final_chart, use_container_width=True)

def getRewatches(df):
    # Calcular los datos del gráfico
    rewatch_counts = df['Rewatch'].fillna('No').value_counts()
    first_time_count = rewatch_counts.get('No', 0)
    rewatch_count = rewatch_counts.get('Yes', 0)
    
    # Crear un DataFrame con los datos
    total = first_time_count + rewatch_count
    data = pd.DataFrame({
        'Category': ['Primera vez', 'Rewatch'],
        'Count': [first_time_count, rewatch_count],
        'Percentage': [first_time_count / total * 100, rewatch_count / total * 100],
        'Color': ['#32CD32', '#006400']  # Verde claro y verde oscuro
    })
    
    # Crear el gráfico de sectores
    chart = alt.Chart(data).mark_arc().encode(
        theta=alt.Theta(field='Count', type='quantitative'),
        color=alt.Color(field='Color', type='nominal', scale=None),
        tooltip=['Category', 'Count', alt.Tooltip('Percentage:Q', format='.1f')]
    ).properties(
        title='Películas vistas por primera vez vs Rewatches',
        width=400,
        height=400
    )

    # Agregar etiquetas visibles
    text = alt.Chart(data).mark_text(radius=120, size=14).encode(
        theta=alt.Theta(field='Count', type='quantitative'),
        text=alt.Text('Percentage:Q', format='.1f%'),
        color=alt.value('white')
    )
    
    # Combinar el gráfico de sectores con las etiquetas
    final_chart = chart + text

    # Mostrar el gráfico en Streamlit
    st.altair_chart(final_chart, use_container_width=True)

def getDistrib(df):
    # df = df.dropna(subset=['Year'])
    counts, bins = np.histogram(df['Year'], bins=20)
    
    # Redondear los valores de los bordes a enteros y crear etiquetas de rango
    bins = bins.astype(int)
    bin_labels = [f"{bins[i]}-{bins[i+1]-1}" for i in range(len(bins)-1)]
    
    # Crear un DataFrame con los resultados
    hist_df = pd.DataFrame({
        'Year Range': bin_labels,
        'Count': counts
    })
    
    # Crear el gráfico con Altair
    chart = alt.Chart(hist_df).mark_bar(color="green").encode(
        x=alt.X('Year Range:N', title='Year Range'),
        y=alt.Y('Count:Q', title='Count'),
        tooltip=['Year Range', 'Count']
    ).properties(
        title="Distribución de películas por año",
        width=700,
        height=400
    )
    
    # Mostrar el gráfico
    st.altair_chart(chart, use_container_width=True)


def get5stars(df):
    df_res = df[df['Rating'] == 5]
    df_res = df_res[['Name','Year', 'valoracion_media', 'Rating', 'Letterboxd URI']].reset_index(drop=True)
    df_res = df_res.rename(columns={'valoracion_media': 'Average Rating', 'Letterboxd URI' : 'Letterboxd URL'})
    df_res['Average Rating'] = df_res['Average Rating'].fillna(0)
    df_res['Year'] = df_res['Year'].astype(int).astype(str)
    st.write("**Las películas que has valorado con 5 estrellas**")
    st.dataframe(df_res)


def getLessPopular(df):
    df_res = df
    df_res['Popularity'] = df['Letterboxd URI'].map(st.session_state.films_popularity)
    df_res['Rating'] = df_res['Rating'].fillna(0)
    df_res['Popularity'].astype(float)
    df_res = df_res[df_res['Popularity'] > -1]

    df_res = df_res.rename(columns={'valoracion_media': 'Average Rating', 'Letterboxd URI' : 'Letterboxd URL'})
    df_res['Year'] = df_res['Year'].astype(int).astype(str)
    df_res = df_res.nsmallest(10, 'Popularity')[['Name','Year', 'Average Rating', 'Rating', 'Letterboxd URL']].reset_index(drop=True)

    st.write("**Las 10 películas menos populares que has visto**")
    st.dataframe(df_res)

def getMorePopular(df):
    df_res = df
    df_res['Popularity'] = df['Letterboxd URI'].map(st.session_state.films_popularity)
    df_res['Rating'] = df_res['Rating'].fillna(0)
    df_res = df_res.rename(columns={'valoracion_media': 'Average Rating', 'Letterboxd URI' : 'Letterboxd URL'})
    df_res['Year'] = df_res['Year'].astype(int).astype(str)
    df_res = df_res.nlargest(10, 'Popularity')[['Name','Year', 'Average Rating', 'Rating', 'Letterboxd URL']].reset_index(drop=True)

    st.write("**Las 10 películas más populares que has visto**")
    st.dataframe(df_res)



def app():
    # Acceder a la variable definida en app.py a través de st.session_state
    if 'dfs' in st.session_state and st.session_state.finished == True:
        st.write(f"**Este año has visto {len(st.session_state.dfs[0])} películas en total**")
        st.session_state.dfs[0] = st.session_state.dfs[0].dropna(subset=['Year'])
        # st.session_state.dfs[0]['Year'] = st.session_state.dfs[0]['Year'].astype(str)
        getTop10(st.session_state.dfs[0])
        getWorst5(st.session_state.dfs[0])
        getDecadas(st.session_state.dfs[0])
        getRewatches(st.session_state.dfs[0])
        getDistrib(st.session_state.dfs[0])
        get5stars(st.session_state.dfs[0])
        getLessPopular(st.session_state.dfs[0])
        getMorePopular(st.session_state.dfs[0])
        # st.write("Vista previa del archivo:")
        # st.dataframe(st.session_state.dfs[0])
    else:
        st.write("Por favor, introduce primero los archivos necesarios")


app()
