# Streamlit app: Seni Kraf Manik PPKI SMK Sultan Muzafar Shah 1 (Kefungsian Rendah)
# Fail ini membolehkan tambah produk, harga, dan muat naik gambar proses pembuatan manik.
# Simpan sebagai `streamlit run streamlit_seni_kraf_bonik.py` untuk jalankan.

import streamlit as st
import pandas as pd
from PIL import Image
import os
from pathlib import Path
import uuid

# --- Konfigurasi ---
st.set_page_config(page_title="Seni Kraf Manik PPKI", layout="wide")
DATA_DIR = Path("./seni_kraf_data")
IMG_DIR = DATA_DIR / "images"
CSV_FILE = DATA_DIR / "products.csv"
DATA_DIR.mkdir(exist_ok=True)
IMG_DIR.mkdir(exist_ok=True)

# Senarai kategori produk default
DEFAULT_CATEGORIES = [
    "Brooch Tudung - Kecil",
    "Brooch Tudung - Sederhana",
    "Brooch Tudung - Besar",
    "Gelang Tangan",
    "Keychain Nama",
    "Cincin",
    "Cincin Tudung",
    "Keychain Bentuk",
    "Tasbih",
]

# --- Utiliti simpan/ambil data ---

def load_products():
    if CSV_FILE.exists():
        return pd.read_csv(CSV_FILE)
    return pd.DataFrame(columns=["id", "nama", "kategori", "harga", "gambar_path", "keterangan"])


def save_products(df: pd.DataFrame):
    df.to_csv(CSV_FILE, index=False)


def save_image(uploaded_file) -> str:
    # simpan image dan return path relatif
    suffix = Path(uploaded_file.name).suffix
    filename = f"{uuid.uuid4().hex}{suffix}"
    dest = IMG_DIR / filename
    with open(dest, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return str(dest)


# --- UI Sidebar ---
with st.sidebar:
    st.title("Seni Kraf Manik")
    st.write("PPKI SMK Sultan Muzafar Shah 1 - Kefungsian Rendah")
    st.markdown("---")
    if st.button("Reset semua data (Hati-hati) 🗑️"):
        # berhati-hati: padam CSV dan gambar
        if st.confirm := st.checkbox:
            pass
        # Simple safety confirm
        confirm = st.text_input("Taip 'DELETE' untuk sahkan:")
        if confirm == "DELETE":
            for p in IMG_DIR.glob("*"):
                p.unlink(missing_ok=True)
            if CSV_FILE.exists():
                CSV_FILE.unlink()
            st.success("Semua data dipadam. Sila refresh aplikasi.")
    st.markdown("---")
    st.write("Tips:")
    st.write("1. Tambah produk dengan nama, kategori dan harga.\n2. Muat naik gambar proses (galeri) secara berasingan.\n3. Gambar akan disimpan di folder 'seni_kraf_data/images'.")

# --- Main Page ---
st.header("Seni Kraf Manik — PPKI SMK Sultan Muzafar Shah 1")
col1, col2 = st.columns([2, 1])

# Column 1: Borang tambah produk & galeri
with col1:
    st.subheader("Tambah / Urus Produk")
    with st.expander("Tambah Produk Baru"):
        with st.form("form_tambah_produK", clear_on_submit=True):
            nama = st.text_input("Nama Produk", placeholder="Contoh: Brooch Tudung - Kecil A")
            kategori = st.selectbox("Kategori", options=DEFAULT_CATEGORIES)
            harga = st.number_input("Harga (RM)", min_value=0.0, step=0.5, format="%.2f")
            keterangan = st.text_area("Keterangan (pilihan)", value="")
            gambar = st.file_uploader("Muat naik gambar produk (pilih 1)", type=["png","jpg","jpeg"], accept_multiple_files=False)
            submitted = st.form_submit_button("Simpan Produk")

            if submitted:
                if not nama.strip():
                    st.error("Sila masukkan nama produk.")
                else:
                    df = load_products()
                    pid = uuid.uuid4().hex
                    gambar_path = ""
                    if gambar is not None:
                        gambar_path = save_image(gambar)
                    new = {"id": pid, "nama": nama, "kategori": kategori, "harga": harga, "gambar_path": gambar_path, "keterangan": keterangan}
                    df = pd.concat([df, pd.DataFrame([new])], ignore_index=True)
                    save_products(df)
                    st.success(f"Produk '{nama}' disimpan.")

    st.markdown("---")
    st.subheader("Galeri Proses Pembuatan (Muat Naik Banyak)")
    uploaded = st.file_uploader("Muat naik gambar proses (boleh pilih banyak)", type=["png","jpg","jpeg"], accept_multiple_files=True)
    if uploaded:
        st.info(f"Menyimpan {len(uploaded)} gambar...")
        saved = []
        for f in uploaded:
            p = save_image(f)
            saved.append(p)
        st.success(f"{len(saved)} gambar disimpan ke galeri.")

    st.markdown("---")
    st.subheader("Galeri (Tunjuk semua gambar yang dimuat naik)")
    imgs = list(IMG_DIR.glob("*"))
    if imgs:
        # Papar 4 setiap baris
        for i in range(0, len(imgs), 4):
            row = imgs[i:i+4]
            cols = st.columns(len(row))
            for c, img_path in zip(cols, row):
                try:
                    im = Image.open(img_path)
                    c.image(im, use_column_width=True, caption=img_path.name)
                except Exception as e:
                    c.write("Gagal buka imej")
    else:
        st.write("Tiada gambar dimuat naik lagi.")

# Column 2: Senarai produk & carian
with col2:
    st.subheader("Senarai Produk")
    df = load_products()
    cat_filter = st.selectbox("Tapis kategori", options=["Semua"] + DEFAULT_CATEGORIES)
    if cat_filter != "Semua":
        display_df = df[df['kategori'] == cat_filter]
    else:
        display_df = df

    # Papar ringkas sebagai grid kad
    if display_df.empty:
        st.info("Tiada produk ditemui.")
    else:
        # Papar cards 2 kolum
        rows = display_df.to_dict(orient="records")
        for i in range(0, len(rows), 2):
            r = rows[i:i+2]
            cols = st.columns(2)
            for col, item in zip(cols, r):
                col.markdown(f"**{item['nama']}**")
                if item.get('gambar_path'):
                    try:
                        img = Image.open(item['gambar_path'])
                        col.image(img, use_column_width=True)
                    except Exception:
                        col.write("Gambar tiada / rosak")
                col.write(f"**Harga:** RM {float(item['harga']):.2f}")
                if item.get('keterangan'):
                    col.write(item['keterangan'])
                # butang untuk padam
                if col.button(f"Padam {item['nama']}", key=f"del_{item['id']}"):
                    df = df[df['id'] != item['id']]
                    # padam gambar jika ada
                    try:
                        if item.get('gambar_path') and Path(item['gambar_path']).exists():
                            Path(item['gambar_path']).unlink()
                    except Exception:
                        pass
                    save_products(df)
                    st.experimental_rerun()

st.markdown("---")

# Paparan penuh jadual dan muat turun
st.subheader("Data Produk (Jadual)")
df_all = load_products()
if not df_all.empty:
    st.dataframe(df_all.drop(columns=['gambar_path']))
    csv_bytes = df_all.to_csv(index=False).encode('utf-8')
    st.download_button("Muat turun CSV produk", data=csv_bytes, file_name="produk_seni_kraf.csv", mime="text/csv")
else:
    st.write("Tiada data produk disimpan.")

st.caption("Dibangunkan untuk tujuan dokumentasi hasil kraf manik PPKI SMK Sultan Muzafar Shah 1. Jika perlukan fungsi tambahan (contoh: pembayaran, borang tempahan, cetak sijil atau etalase yang lebih menarik), beri tahu saya dan saya kemaskini kod ini.")
