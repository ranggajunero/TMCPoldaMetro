import streamlit as st
import pandas as pd
import json
import plotly.express as px

st.set_page_config(layout="wide")
st.title("Dashboard Lalu Lintas Jakarta")

# Load JSON
with open("hasil_rule_base_inner_TMCPoldaMetro.json") as f:
    data = json.load(f)

df = pd.DataFrame(data)

# Pie chart status lalu lintas
st.subheader("Distribusi Status Lalu Lintas")
status_count = df["STATUS"].dropna().value_counts()
fig = px.pie(
    names=status_count.index,
    values=status_count.values,
    title="Status Lalu Lintas"
)
st.plotly_chart(fig, use_container_width=True)

# Bar chart lokasi asal terbanyak
st.subheader("10 Lokasi Asal Terbanyak")
from_count = df["FROM"].dropna().value_counts().nlargest(10)
fig2 = px.bar(
    x=from_count.index,
    y=from_count.values,
    labels={"x": "Lokasi", "y": "Jumlah"},
    title="Top 10 Lokasi FROM"
)
st.plotly_chart(fig2, use_container_width=True)

# Tabel data
st.subheader("Data Lalu Lintas Mentah")
st.dataframe(df)
