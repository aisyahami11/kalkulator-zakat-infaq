"""
app.py - Antarmuka Streamlit Kalkulator Zakat dan Pencatat Infaq
Peran 3: Pengembang Antarmuka dan Deploy (Kelompok 19, DDP)

Jalankan dengan:  streamlit run app.py
Semua perhitungan dan validasi ada di logika.py; file ini hanya
menampilkan form, hasil, dan pesan kesalahan.
"""

from datetime import date

import streamlit as st

from logika import (
    KONFIGURASI,
    PencatatInfaq,
    ZakatFitrah,
    ZakatMal,
    ZakatPenghasilan,
    cek_nisab,
    format_rupiah,
)

# ---------------------------------------------------------------------------
# Pengaturan halaman
# ---------------------------------------------------------------------------
st.set_page_config(page_title="Kalkulator Zakat & Pencatat Infaq", page_icon="🕌")

# Data infaq disimpan selama sesi (tanpa database)
if "pencatat" not in st.session_state:
    st.session_state["pencatat"] = PencatatInfaq()
pencatat = st.session_state["pencatat"]


# ---------------------------------------------------------------------------
# Fungsi tampilan
# ---------------------------------------------------------------------------
def tampilan_form(judul, keterangan=None):
    """Tampilkan judul halaman dan keterangan singkat."""
    st.header(judul)
    if keterangan:
        st.caption(keterangan)


def tampilkan_hasil(hasil):
    """Tampilkan dictionary hasil hitung() dari modul logika."""
    if hasil["wajib"]:
        st.success(hasil["pesan"])
    else:
        st.info(hasil["pesan"])

    kolom1, kolom2 = st.columns(2)
    kolom1.metric("Nisab", format_rupiah(hasil["nisab"]))
    kolom2.metric("Zakat yang dibayar", format_rupiah(hasil["zakat"]))


def tampilkan_error(pesan):
    """Tampilkan pesan hasil validasi dari modul logika."""
    st.error(pesan)


# ---------------------------------------------------------------------------
# Sidebar: menu dan parameter
# ---------------------------------------------------------------------------
st.title("🕌 Kalkulator Zakat dan Pencatat Infaq")

menu = st.sidebar.radio(
    "Menu",
    [
        "Zakat Penghasilan",
        "Zakat Mal",
        "Zakat Fitrah",
        "Cek Nisab",
        "Catat Infaq",
        "Rekap Infaq per Pekan",
    ],
)

st.sidebar.markdown("---")
st.sidebar.subheader("Parameter")
st.sidebar.caption(
    "Perbarui sesuai rilis resmi BAZNAS sebelum dipakai. Nilai awal hanya contoh."
)
harga_emas = st.sidebar.number_input(
    "Harga emas per gram (Rp)", min_value=0.0, value=1_500_000.0, step=10_000.0
)
harga_beras = st.sidebar.number_input(
    "Harga beras per kg (Rp)", min_value=0.0, value=15_000.0, step=500.0
)

# ---------------------------------------------------------------------------
# Halaman
# ---------------------------------------------------------------------------
if menu == "Zakat Penghasilan":
    tampilan_form(
        "Zakat Penghasilan",
        "Zakat 2,5% jika penghasilan bulanan mencapai nisab bulanan.",
    )
    penghasilan = st.number_input(
        "Penghasilan bulanan (Rp)", min_value=0.0, value=0.0, step=100_000.0
    )
    if st.button("Hitung zakat penghasilan"):
        try:
            tampilkan_hasil(ZakatPenghasilan().hitung(penghasilan, harga_emas))
        except ValueError as e:
            tampilkan_error(str(e))

elif menu == "Zakat Mal":
    tampilan_form(
        "Zakat Mal",
        f"Wajib jika harta mencapai nisab ({KONFIGURASI['nisab_emas_gram']} gram emas) "
        "dan sudah dimiliki satu tahun (haul).",
    )
    total_harta = st.number_input(
        "Total harta simpanan (Rp)", min_value=0.0, value=0.0, step=1_000_000.0
    )
    status_haul = st.radio(
        "Apakah harta sudah dimiliki selama satu tahun (haul)?", ["Ya", "Tidak"]
    )
    if st.button("Hitung zakat mal"):
        try:
            tampilkan_hasil(
                ZakatMal().hitung(total_harta, harga_emas, status_haul == "Ya")
            )
        except ValueError as e:
            tampilkan_error(str(e))

elif menu == "Zakat Fitrah":
    tampilan_form(
        "Zakat Fitrah",
        f"{KONFIGURASI['beras_per_jiwa_kg']:g} kg beras per jiwa "
        "(harga beras diatur di sidebar).",
    )
    jumlah_jiwa = st.number_input("Jumlah jiwa", min_value=0, value=0, step=1)
    if st.button("Hitung zakat fitrah"):
        try:
            tampilkan_hasil(ZakatFitrah().hitung(jumlah_jiwa, harga_beras))
        except ValueError as e:
            tampilkan_error(str(e))

elif menu == "Cek Nisab":
    tampilan_form(
        "Cek Nisab", "Periksa apakah nilai harta atau penghasilan sudah mencapai nisab."
    )
    jenis_cek = st.radio(
        "Yang diperiksa", ["Harta (nisab tahunan)", "Penghasilan (nisab bulanan)"]
    )
    nilai = st.number_input("Nilai (Rp)", min_value=0.0, value=0.0, step=100_000.0)
    if st.button("Cek nisab"):
        if harga_emas <= 0:
            tampilkan_error("Harga emas per gram harus lebih besar dari 0.")
        elif nilai <= 0:
            tampilkan_error("Nilai harus lebih besar dari 0.")
        else:
            nisab = KONFIGURASI["nisab_emas_gram"] * harga_emas
            if jenis_cek.startswith("Penghasilan"):
                nisab = nisab / KONFIGURASI["bulan_dalam_setahun"]
            if cek_nisab(nilai, nisab):
                st.success(
                    f"{format_rupiah(nilai)} sudah mencapai nisab ({format_rupiah(nisab)})."
                )
            else:
                st.info(
                    f"{format_rupiah(nilai)} belum mencapai nisab ({format_rupiah(nisab)})."
                )

elif menu == "Catat Infaq":
    tampilan_form("Catat Infaq", "Data tersimpan selama sesi penggunaan berjalan.")
    tanggal = st.date_input("Tanggal", value=date.today())
    donatur = st.text_input("Nama donatur")
    jumlah = st.number_input(
        "Jumlah infaq (Rp)", min_value=0.0, value=0.0, step=10_000.0
    )
    if st.button("Simpan infaq"):
        try:
            data = pencatat.catat(tanggal, donatur, jumlah)
            st.success(
                f"Tersimpan: {data['donatur']} - {format_rupiah(data['jumlah'])} "
                f"({data['tanggal']})."
            )
        except ValueError as e:
            tampilkan_error(str(e))

    if pencatat.transaksi:
        st.subheader("Transaksi tercatat")
        st.dataframe(
            [
                {
                    "Tanggal": str(t["tanggal"]),
                    "Donatur": t["donatur"],
                    "Jumlah (Rp)": format_rupiah(t["jumlah"]),
                }
                for t in pencatat.transaksi
            ],
            use_container_width=True,
        )

elif menu == "Rekap Infaq per Pekan":
    tampilan_form("Rekap Infaq per Pekan", "Pekan mengikuti penomoran ISO (Senin-Minggu).")
    if not pencatat.transaksi:
        st.info("Belum ada data infaq. Catat infaq terlebih dahulu di menu Catat Infaq.")
    else:
        rekap = pencatat.rekap_per_pekan()
        st.dataframe(
            [
                {"Pekan": pekan, "Total (Rp)": format_rupiah(total)}
                for pekan, total in rekap.items()
            ],
            use_container_width=True,
        )
        st.metric("Total keseluruhan", format_rupiah(pencatat.total_keseluruhan()))
        if st.button("Hapus semua data infaq"):
            pencatat.hapus_semua()
            st.rerun()

st.markdown("---")
st.caption(
    "Aplikasi ini hanya alat bantu perhitungan, bukan pengganti fatwa atau "
    "konsultasi dengan amil."
)
