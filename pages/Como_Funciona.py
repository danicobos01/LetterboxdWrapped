import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

def app():
    st.write("1. Desde settings en tu perfil de letterboxd vas a la sección de **Data** y exportas tus datos:")
    st.image("tutoletterboxd.PNG")
    st.write("2. Descomprimes el ZIP y en la página introduces sólo los dos archivos mencionados:")
    st.image("tutoletterboxd2.PNG")
    st.write("3. Una vez se cargan, pulsas el botón y termina de cargar ya puedes acceder a las pestañas de la derecha!")

app()