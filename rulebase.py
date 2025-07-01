import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# --- Konfigurasi Halaman ---
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

def plot_laporan_per_jam(df, chart_type='Bar Chart'):
    """Membuat dan menampilkan bar chart ATAU line chart laporan per jam."""
    st.subheader("1. Frekuensi Laporan per Jam")
    jam_counts = df['JAM'].dropna().value_counts().sort_index()
    jam_range = pd.Series(0, index=np.arange(0, 24))
    jam_counts_full = (jam_counts + jam_range).fillna(0).astype(int)
    
    if chart_type == 'Bar Chart':
        fig = px.bar(x=jam_counts_full.index, y=jam_counts_full.values, labels={"x": "Jam (0–23)", "y": "Jumlah Laporan"}, title="Jumlah Laporan Lalu Lintas per Jam")
    elif chart_type == 'Line Chart':
        fig = px.line(x=jam_counts_full.index, y=jam_counts_full.values, labels={"x": "Jam (0–23)", "y": "Jumlah Laporan"}, title="Tren Laporan Lalu Lintas per Jam", markers=True)
    
    fig.update_xaxes(dtick=1)
    st.plotly_chart(fig, use_container_width=True)

# === MODIFIKASI #1: Fungsi diubah untuk menangani Pie atau Bar Chart ===
def plot_status_distribution(df, chart_type='Pie Chart'):
    """Membuat dan menampilkan pie chart ATAU bar chart distribusi status."""
    st.subheader("2. Distribusi Status Lalu Lintas")
    status_count = df["STATUS"].dropna().value_counts()
    
    if chart_type == 'Pie Chart':
        fig = px.pie(names=status_count.index, values=status_count.values, title="Distribusi Status Lalu Lintas", hole=0.3)
        fig.update_traces(textposition='inside', textinfo='percent+label')
    elif chart_type == 'Bar Chart':
        fig = px.bar(x=status_count.index, y=status_count.values, labels={"x": "Status", "y": "Jumlah Laporan"}, title="Jumlah Laporan per Status")
        
    st.plotly_chart(fig, use_container_width=True)

# === MODIFIKASI #2: Fungsi diubah untuk menangani Bar Horizontal atau Vertikal ===
def plot_top_lokasi(df, title, chart_type='Bar Horizontal'):
    """Membuat dan menampilkan bar chart (horizontal/vertikal) untuk top 10 lokasi."""
    st.subheader(title)
    lokasi_count = df["FROM"].dropna().value_counts().nlargest(10)
    if not lokasi_count.empty:
        if chart_type == 'Bar Horizontal':
            fig = px.bar(x=lokasi_count.values, y=lokasi_count.index, orientation='h', labels={"x": "Jumlah Laporan", "y": "Lokasi"}, title=title)
            fig.update_layout(yaxis={'categoryorder':'total ascending'})
        elif chart_type == 'Bar Vertikal':
            fig = px.bar(x=lokasi_count.index, y=lokasi_count.values, labels={"x": "Lokasi", "y": "Jumlah Laporan"}, title=title)
            fig.update_layout(xaxis={'categoryorder':'total descending'})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Tidak ada data lokasi untuk filter yang dipilih.")

# === MODIFIKASI #3: Fungsi diubah untuk menangani Bar Horizontal atau Vertikal ===
def plot_penyebab_kemacetan(df, chart_type='Bar Horizontal'):
    """Membuat dan menampilkan bar chart (horizontal/vertikal) untuk penyebab kemacetan."""
    st.subheader("Penyebab Kemacetan (Obstacle)")
    obstacle_count = df["OBSTACLE"].dropna().value_counts().nlargest(15)
    if not obstacle_count.empty:
        if chart_type == 'Bar Horizontal':
            fig = px.bar(x=obstacle_count.values, y=obstacle_count.index, orientation='h', labels={"x": "Jumlah Kejadian", "y": "Jenis Hambatan"}, title="Top 15 Jenis Hambatan")
            fig.update_layout(yaxis={'categoryorder':'total ascending'})
        elif chart_type == 'Bar Vertikal':
            fig = px.bar(x=obstacle_count.index, y=obstacle_count.values, labels={"x": "Jenis Hambatan", "y": "Jumlah Kejadian"}, title="Top 15 Jenis Hambatan")
            fig.update_layout(xaxis={'categoryorder':'total descending'})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Tidak ada data hambatan untuk filter yang dipilih.")

# ====================================================================
# === APLIKASI UTAMA STREAMLIT ===
# ====================================================================

st.title("🚦 Dashboard Analisis Lalu Lintas Jakarta")

df = load_data("hasil_rule_base_inner_TMCPoldaMetro.json")

if df is not None:
    # --- Sidebar untuk Filter dan Opsi ---
    st.sidebar.header("Filter Data")
    status_pilihan = st.sidebar.multiselect("Pilih Status Lalu Lintas:", options=["Semua Status"] + list(df['STATUS'].dropna().unique()), default="Semua Status")
    obstacle_pilihan = st.sidebar.multiselect("Pilih Jenis Hambatan:", options=["Semua Hambatan"] + list(df['OBSTACLE'].dropna().unique()), default="Semua Hambatan")
    jam_pilihan = st.sidebar.slider("Pilih Rentang Jam:", min_value=0, max_value=23, value=(0, 23))
    st.sidebar.info(f"Data ditampilkan untuk jam {jam_pilihan[0]}:00 hingga {jam_pilihan[1]}:59.")
    
    # === MODIFIKASI #4: Tambahkan widget pilihan untuk semua chart ===
    st.sidebar.markdown("---")
    st.sidebar.subheader("Opsi Visualisasi")
    tipe_chart_jam = st.sidebar.selectbox("Grafik Laporan per Jam:", ('Bar Chart', 'Line Chart'))
    tipe_chart_status = st.sidebar.selectbox("Grafik Distribusi Status:", ('Pie Chart', 'Bar Chart'))
    tipe_chart_lokasi = st.sidebar.selectbox("Grafik Top Lokasi:", ('Bar Horizontal', 'Bar Vertikal'))
    tipe_chart_obstacle = st.sidebar.selectbox("Grafik Penyebab Kemacetan:", ('Bar Horizontal', 'Bar Vertikal'))

    # --- Logika Filter Berantai ---
    df_filtered = df
    if "Semua Status" not in status_pilihan and status_pilihan: df_filtered = df_filtered[df_filtered['STATUS'].isin(status_pilihan)]
    if "Semua Hambatan" not in obstacle_pilihan and obstacle_pilihan: df_filtered = df_filtered[df_filtered['OBSTACLE'].isin(obstacle_pilihan)]
    df_filtered = df_filtered[df_filtered['JAM'].between(jam_pilihan[0], jam_pilihan[1])]

    # --- Tampilan Utama Dashboard ---
    st.header("Visualisasi Data")
    col1, col2 = st.columns(2)
    
    with col1:
        # Teruskan pilihan pengguna ke fungsi plot
        plot_laporan_per_jam(df_filtered, chart_type=tipe_chart_jam)
        plot_top_lokasi(df_filtered, "Top 10 Lokasi untuk Filter Terpilih", chart_type=tipe_chart_lokasi)

    with col2:
        # Pie chart tetap pakai df utuh agar proporsinya terlihat jelas
        plot_status_distribution(df, chart_type=tipe_chart_status)
        plot_penyebab_kemacetan(df_filtered, chart_type=tipe_chart_obstacle)

    # --- Tampilkan Data Mentah ---
    st.subheader("Tabel Data Laporan (Hasil Filter)")
    st.info(f"Menampilkan {len(df_filtered)} baris dari total {len(df)} laporan.")
    st.dataframe(df_filtered)
