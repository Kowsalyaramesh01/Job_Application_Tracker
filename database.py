import mysql.connector
import streamlit as st


def get_connection():
    connection = mysql.connector.connect(
        host=st.secrets["DB_HOST"],
        port=int(st.secrets["DB_PORT"]),
        user=st.secrets["DB_USER"],
        password=st.secrets["DB_PASSWORD"],
        database=st.secrets["DB_NAME"],
        ssl_verify_cert=True,
        ssl_verify_identity=True,
    )

    return connection