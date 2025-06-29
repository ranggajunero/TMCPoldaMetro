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

# Ubah kolom TIME ke datetime agar bisa ambil jam
df["JAM"] = pd.to_datetime(df["TIME"], format="%H:%M:%S").dt.hour

# --- Visualisasi 1: Frekuensi laporan per jam (0–23 lengkap) ---
st.subheader("1. Frekuensi Laporan per Jam")

# Konversi ke datetime jam
df["JAM"] = pd.to_datetime(df["TIME"], format="%H:%M:%S").dt.hour

# Buat urutan jam 0–23
all_hours = pd.Series(range(24), name="JAM")
jam_count = df["JAM"].value_counts().sort_index()
jam_count_full = all_hours.to_frame().merge(
    jam_count.rename("Jumlah"), on="JAM", how="left"
).fillna(0)

# Grafik
fig_jam = px.bar(
    jam_count_full,
    x="JAM",
    y="Jumlah",
    labels={"JAM": "Jam", "Jumlah": "Jumlah Laporan"},
    title="Jumlah Laporan Lalu Lintas per Jam (0–23)",
)
fig_jam.update_xaxes(dtick=1)  # Tampilkan semua jam
st.plotly_chart(fig_jam, use_container_width=True)

# ---- Visualisasi 2: Lokasi paling padat (berdasarkan status padat) ----
st.subheader("2. Lokasi Paling Padat")
lokasi_padat = df[df["STATUS"].str.contains("padat", case=False, na=False)]
lokasi_count = lokasi_padat["FROM"].value_counts().nlargest(10)
fig_lokasi = px.bar(
    x=lokasi_count.index,
    y=lokasi_count.values,
    labels={"x": "Lokasi", "y": "Frekuensi"},
    title="Top 10 Lokasi dengan Kepadatan Tertinggi"
)
st.plotly_chart(fig_lokasi, use_container_width=True)

# ---- Visualisasi 3: Jenis Kejadian (Status Lalu Lintas) ----
st.subheader("3. Distribusi Status Lalu Lintas")
status_count = df["STATUS"].dropna().value_counts()
fig_status = px.pie(
    names=status_count.index,
    values=status_count.values,
    title="Distribusi Jenis Kejadian / Status Lalu Lintas"
)
st.plotly_chart(fig_status, use_container_width=True)

# ---- Visualisasi 4: Penyebab Kemacetan (OBSTACLE) ----
st.subheader("4. Penyebab Kemacetan")
obstacle_count = df["OBSTACLE"].dropna().value_counts()
fig_obstacle = px.bar(
    x=obstacle_count.index,
    y=obstacle_count.values,
    labels={"x": "Penyebab", "y": "Jumlah"},
    title="Top Penyebab Kemacetan"
)
st.plotly_chart(fig_obstacle, use_container_width=True)


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
