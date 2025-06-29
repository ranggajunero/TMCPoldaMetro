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
# @st.cache_data akan menyimpan hasil dari fungsi ini di memori.
# Artinya, Streamlit tidak akan memuat ulang file JSON setiap kali ada interaksi,
# membuat dashboard berjalan jauh lebih cepat!
@st.cache_data
def load_data(file_path):
    """Memuat data dari file JSON dan melakukan pra-pemrosesan dasar."""
    try:
        df = pd.read_json(file_path)
        # Mengubah kolom waktu menjadi format datetime untuk diolah
        df['TIME_dt'] = pd.to_datetime(df['TIME'], format='%H:%M:%S', errors='coerce')
        # Membuat kolom baru berisi jam (0-23)
        df['JAM'] = df['TIME_dt'].dt.hour
        return df
    except FileNotFoundError:
        st.error(f"Error: File '{file_path}' tidak ditemukan. Pastikan file berada di direktori yang sama.")
        return None
    except Exception as e:
        st.error(f"Terjadi error saat memuat data: {e}")
        return None

# --- Fungsi-fungsi untuk Membuat Plot/Grafik ---
# Membungkus setiap grafik dalam fungsinya sendiri membuat kode utama lebih bersih.

def plot_laporan_per_jam(df):
    """Membuat dan menampilkan bar chart laporan per jam."""
    st.subheader("1. Frekuensi Laporan per Jam")
    
    # Menghitung jumlah laporan per jam, pastikan semua jam (0-23) ada
    jam_counts = df['JAM'].value_counts().sort_index()
    jam_range = pd.Series(0, index=np.arange(0, 24))
    jam_counts_full = (jam_counts + jam_range).fillna(0).astype(int)

    fig = px.bar(
        x=jam_counts_full.index,
        y=jam_counts_full.values,
        labels={"x": "Jam (0–23)", "y": "Jumlah Laporan"},
        title="Jumlah Laporan Lalu Lintas per Jam"
    )
    fig.update_xaxes(dtick=1)
    st.plotly_chart(fig, use_container_width=True)

def plot_status_pie(df):
    """Membuat dan menampilkan pie chart distribusi status."""
    st.subheader("2. Distribusi Status Lalu Lintas")
    status_count = df["STATUS"].dropna().value_counts()
    fig = px.pie(
        names=status_count.index,
        values=status_count.values,
        title="Distribusi Status Lalu Lintas",
        hole=0.3 # Membuatnya terlihat seperti Donut Chart
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig, use_container_width=True)

def plot_top_lokasi(df, title="Top 10 Lokasi Laporan"):
    """Membuat dan menampilkan bar chart untuk top 10 lokasi."""
    st.subheader(title)
    lokasi_count = df["FROM"].dropna().value_counts().nlargest(10)
    if not lokasi_count.empty:
        fig = px.bar(
            x=lokasi_count.values,
            y=lokasi_count.index,
            orientation='h', # Membuat bar chart horizontal agar mudah dibaca
            labels={"x": "Jumlah Laporan", "y": "Lokasi"},
            title=title
        )
        fig.update_layout(yaxis={'categoryorder':'total ascending'}) # Urutkan dari yg terbanyak
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Tidak ada data lokasi untuk status yang dipilih.")

def plot_penyebab_kemacetan(df):
    """Membuat dan menampilkan bar chart untuk penyebab kemacetan (obstacle)."""
    st.subheader("Penyebab Kemacetan (Obstacle)")
    obstacle_count = df["OBSTACLE"].dropna().value_counts().nlargest(15)
    if not obstacle_count.empty:
        fig = px.bar(
            x=obstacle_count.values,
            y=obstacle_count.index,
            orientation='h',
            labels={"x": "Jumlah Kejadian", "y": "Jenis Hambatan"},
            title="Top 15 Jenis Hambatan"
        )
        fig.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Tidak ada data hambatan (obstacle) yang tercatat.")

# ====================================================================
# === APLIKASI UTAMA STREAMLIT ===
# ====================================================================

st.title("🚦 Dashboard Analisis Lalu Lintas Jakarta")

# Memuat data menggunakan fungsi yang sudah di-cache
df = load_data("laporan_lalulintas_hasil.json") # Ganti nama file jika berbeda

if df is not None:
    # --- Sidebar untuk Filter ---
    st.sidebar.header("Filter Data")
    
    # Filter berdasarkan status lalu lintas
    # Ambil semua status unik dari data, tambahkan opsi "Semua Status"
    status_unik = df['STATUS'].dropna().unique()
    status_pilihan = st.sidebar.multiselect(
        "Pilih Status Lalu Lintas:",
        options=["Semua Status"] + list(status_unik),
        default="Semua Status"
    )

    # Filter DataFrame berdasarkan pilihan pengguna
    if "Semua Status" in status_pilihan or not status_pilihan:
        df_filtered = df # Jika memilih "Semua" atau tidak memilih apa-apa, gunakan semua data
    else:
        df_filtered = df[df['STATUS'].isin(status_pilihan)]

    st.header("Visualisasi Data")
    
    # --- Tampilkan Visualisasi dalam Kolom ---
    # Membuat dua kolom utama
    col1, col2 = st.columns(2)

    with col1:
        plot_laporan_per_jam(df_filtered)
        plot_top_lokasi(df_filtered, f"Top 10 Lokasi dengan Status: {', '.join(status_pilihan)}")

    with col2:
        plot_status_pie(df) # Pie chart menampilkan distribusi keseluruhan, jadi pakai df asli
        plot_penyebab_kemacetan(df_filtered)

    # --- Tampilkan Data Mentah ---
    st.subheader("Tabel Data Laporan")
    st.info(f"Menampilkan {len(df_filtered)} baris dari total {len(df)} laporan.")
    # Menggunakan st.dataframe agar tabel lebih interaktif
    st.dataframe(df_filtered)
