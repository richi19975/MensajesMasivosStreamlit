import streamlit as st
import pandas as pd
from telethon import TelegramClient
from telethon.errors import PeerIdInvalidError, UserPrivacyRestrictedError
import asyncio
import os
import time

# Configurar las credenciales de Telegram
api_id = '21303180'
api_hash = 'cde3b0d89333b9821c557f3ef3d52a0a'
phone = '+59175810102'

# Función para enviar mensajes
async def enviar_mensajes(data_filtrada, imagen_path):
    start_time = time.time()
    client = TelegramClient('session_name', api_id, api_hash)
    await client.start(phone)
    
    for _, row in data_filtrada.iterrows():
        numero = row['Número']
        vendedor = row['Vendedor']
        mensaje = f"Hola {vendedor}, aquí están los descuentos y promociones para tu ruta {row['Ruta']}."

        try:
            receiver = await client.get_entity(numero)
            await client.send_message(receiver, mensaje)
            await client.send_file(receiver, imagen_path)
            st.success(f"Mensaje enviado a {vendedor} ({numero}).")
        except PeerIdInvalidError:
            st.error(f"Error: El número {numero} no está disponible en Telegram.")
        except UserPrivacyRestrictedError:
            st.error(f"Error: {numero} tiene restricciones de privacidad.")
        except Exception as e:
            st.error(f"Error inesperado al enviar a {vendedor} ({numero}): {e}")
    
    await client.disconnect()
    st.write(f"Mensajes enviados y cliente desconectado. Tiempo total: {time.time() - start_time:.2f} segundos.")

# Interfaz de usuario con Streamlit
st.title("Envío de Mensajes Masivos por Telegram")

# Paso 1: Subir archivo Excel
excel_file = st.file_uploader("Sube el archivo Excel", type=["xlsx"])
if excel_file:
    data = pd.read_excel(excel_file)
    data['Ciudad'] = data['Ciudad'].str.strip().str.lower()
    data['Canal'] = data['Canal'].astype(str).str.strip()
    data['Ruta'] = data['Ruta'].str.strip().str.lower()
    data['Número'] = data['Número'].astype(str).str.strip()
    data['Vendedor'] = data['Vendedor'].str.strip()
    
    st.write("Datos cargados correctamente:")
    st.dataframe(data)

    # Paso 2: Filtrar datos
    ciudad = st.text_input("Filtrar por ciudad (opcional):").strip().lower()
    canal = st.text_input("Filtrar por canal (opcional):").strip()
    ruta = st.text_input("Filtrar por ruta (opcional):").strip().lower()

    filtros = []
    if ciudad:
        filtros.append(data['Ciudad'] == ciudad)
    if canal:
        filtros.append(data['Canal'] == canal)
    if ruta:
        filtros.append(data['Ruta'] == ruta)

    if filtros:
        data_filtrada = data.loc[pd.concat(filtros, axis=1).all(axis=1)]
    else:
        data_filtrada = data

    if not data_filtrada.empty:
        st.write("Vendedores seleccionados:")
        st.dataframe(data_filtrada)

        # Paso 3: Subir imagen
        imagen_file = st.file_uploader("Sube la imagen a enviar", type=["jpg", "jpeg", "png"])
        if imagen_file:
            imagen_path = f"temp_{imagen_file.name}"
            with open(imagen_path, "wb") as f:
                f.write(imagen_file.getbuffer())
            st.success("Imagen cargada correctamente.")

            # Paso 4: Enviar mensajes
            if st.button("Enviar mensajes"):
                asyncio.run(enviar_mensajes(data_filtrada, imagen_path))
                os.remove(imagen_path)
    else:
        st.error("No se encontraron vendedores con los criterios especificados.")
