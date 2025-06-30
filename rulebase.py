import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# --- Konfigurasi Halaman (selalu di baris pertama) ---
st.set_page_config(
    layout="wide",
    page_title="Dashboard Lalu Lintas Jakarta",
    page_icon="🚦"
)

# --- Fungsi untuk Memuat Data (dengan Caching) ---
@st.cache_data
def load_data(file_path):
    """Memuat data dari file JSON dan melakukan pra-pemrosesan dasar."""
    try:
        df = pd.read_json(file_path)
        df['TIME_dt'] = pd.to_datetime(df['TIME'], format='%H:%M:%S', errors='coerce')
        df['JAM'] = df['TIME_dt'].dt.hour
        return df
    except FileNotFoundError:
        st.error(f"Error: File '{file_path}' tidak ditemukan. Pastikan file berada di direktori yang sama.")
        return None
    except Exception as e:
        st.error(f"Terjadi error saat memuat data: {e}")
        return None

# --- Fungsi-fungsi untuk Membuat Plot/Grafik ---
# (Tidak ada perubahan di sini, semua fungsi plot tetap sama)
def plot_laporan_per_jam(df):
    st.subheader("1. Frekuensi Laporan per Jam")
    jam_counts = df['JAM'].dropna().value_counts().sort_index()
    jam_range = pd.Series(0, index=np.arange(0, 24))
    jam_counts_full = (jam_counts + jam_range).fillna(0).astype(int)
    fig = px.bar(x=jam_counts_full.index, y=jam_counts_full.values, labels={"x": "Jam (0–23)", "y": "Jumlah Laporan"}, title="Jumlah Laporan Lalu Lintas per Jam")
    fig.update_xaxes(dtick=1)
    st.plotly_chart(fig, use_container_width=True)

def plot_status_pie(df):
    st.subheader("2. Distribusi Status Lalu Lintas")
    status_count = df["STATUS"].dropna().value_counts()
    fig = px.pie(names=status_count.index, values=status_count.values, title="Distribusi Status Lalu Lintas", hole=0.3)
    fig.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig, use_container_width=True)

def plot_top_lokasi(df, title="Top 10 Lokasi Laporan"):
    st.subheader(title)
    lokasi_count = df["FROM"].dropna().value_counts().nlargest(10)
    if not lokasi_count.empty:
        fig = px.bar(x=lokasi_count.values, y=lokasi_count.index, orientation='h', labels={"x": "Jumlah Laporan", "y": "Lokasi"}, title=title)
        fig.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Tidak ada data lokasi untuk filter yang dipilih.")

def plot_penyebab_kemacetan(df):
    st.subheader("Penyebab Kemacetan (Obstacle)")
    obstacle_count = df["OBSTACLE"].dropna().value_counts().nlargest(15)
    if not obstacle_count.empty:
        fig = px.bar(x=obstacle_count.values, y=obstacle_count.index, orientation='h', labels={"x": "Jumlah Kejadian", "y": "Jenis Hambatan"}, title="Top 15 Jenis Hambatan")
        fig.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Tidak ada data hambatan untuk filter yang dipilih.")

# ====================================================================
# === APLIKASI UTAMA STREAMLIT ===
# ====================================================================

st.title("🚦 Dashboard Analisis Lalu Lintas Jakarta")

# Memuat data menggunakan fungsi yang sudah di-cache
df = load_data("laporan_lalulintas_hasil.json") # Ganti nama file jika berbeda

if df is not None:
    # --- Sidebar untuk Filter ---
    st.sidebar.header("Filter Data")
    
    # --- BLOK FILTER BARU ---
    
    # Filter 1: Berdasarkan status lalu lintas
    status_unik = df['STATUS'].dropna().unique()
    status_pilihan = st.sidebar.multiselect(
        "Pilih Status Lalu Lintas:",
        options=["Semua Status"] + list(status_unik),
        default="Semua Status"
    )

    # Filter 2: Berdasarkan penyebab (obstacle)
    obstacle_unik = df['OBSTACLE'].dropna().unique()
    obstacle_pilihan = st.sidebar.multiselect(
        "Pilih Jenis Hambatan:",
        options=["Semua Hambatan"] + list(obstacle_unik),
        default="Semua Hambatan"
    )

    # Filter 3: Berdasarkan rentang jam
    jam_pilihan = st.sidebar.slider(
        "Pilih Rentang Jam:",
        min_value=0,
        max_value=23,
        value=(0, 23) # Defaultnya adalah seluruh jam
    )
    st.sidebar.info(f"Data ditampilkan untuk jam {jam_pilihan[0]}:00 hingga {jam_pilihan[1]}:59.")
    
    # --- LOGIKA FILTER BERANTAI ---
    # Mulai dengan DataFrame utuh
    df_filtered = df

    # Terapkan filter status
    if "Semua Status" not in status_pilihan and status_pilihan:
        df_filtered = df_filtered[df_filtered['STATUS'].isin(status_pilihan)]

    # Terapkan filter obstacle pada hasil filter sebelumnya
    if "Semua Hambatan" not in obstacle_pilihan and obstacle_pilihan:
        df_filtered = df_filtered[df_filtered['OBSTACLE'].isin(obstacle_pilihan)]
        
    # Terapkan filter jam pada hasil filter sebelumnya
    # .between() sangat efisien untuk rentang numerik
    df_filtered = df_filtered[df_filtered['JAM'].between(jam_pilihan[0], jam_pilihan[1])]

    # --- Tampilan Utama Dashboard ---
    st.header("Visualisasi Data")
    
    # Membuat dua kolom utama
    col1, col2 = st.columns(2)

    with col1:
        plot_laporan_per_jam(df_filtered)
        plot_top_lokasi(df_filtered, f"Top 10 Lokasi untuk Filter Terpilih")

    with col2:
        # Pie chart tetap menampilkan distribusi keseluruhan agar ada perbandingan
        plot_status_pie(df) 
        plot_penyebab_kemacetan(df_filtered)

    # Tampilkan Data Mentah yang sudah difilter
    st.subheader("Tabel Data Laporan (Hasil Filter)")
    st.info(f"Menampilkan {len(df_filtered)} baris dari total {len(df)} laporan.")
    st.dataframe(df_filtered)
