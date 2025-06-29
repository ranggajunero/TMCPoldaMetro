import streamlit as st
import pandas as pd
import json
import plotly.express as px

st.title("Dashboard Lalu Lintas Jakarta")

# Load JSON
with open("hasil_rule_base_inner_TMCPoldaMetro.json") as f:
    data = json.load(f)

df = pd.DataFrame(data)

# Pie chart status
st.subheader("Distribusi Status Lalu Lintas")
status_count = df["STATUS"].dropna().value_counts()
fig = px.pie(names=status_count.index, values=status_count.values)
st.plotly_chart(fig)

# Tabel data mentah
st.subheader("Data Mentah")
st.dataframe(df)
