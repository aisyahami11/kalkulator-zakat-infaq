"""
logika.py - Modul logika Kalkulator Zakat dan Pencatat Infaq
Peran 2: Pengembang Logika (Kelompok 19, DDP)

Kesepakatan tim:
- hitung() mengembalikan dictionary dengan kunci: jenis, wajib, nisab, zakat, pesan.
- Validasi input dilakukan di modul ini. Input tidak valid -> ValueError
  dengan pesan yang siap ditampilkan oleh antarmuka (app.py).
- Nilai nisab, harga emas, dan harga beras TIDAK ditulis langsung di rumus.
  Semuanya diambil dari konfigurasi (KONFIGURASI) atau input pengguna.
"""

from datetime import date, datetime

# ---------------------------------------------------------------------------
# KONFIGURASI
# Perbarui sesuai rilis resmi BAZNAS sebelum aplikasi dipakai/dipresentasikan.
# ---------------------------------------------------------------------------
KONFIGURASI = {
    "nisab_emas_gram": 85,        # nisab zakat mal & penghasilan = 85 gram emas
    "kadar_zakat": 0.025,         # 2,5%
    "beras_per_jiwa_kg": 2.5,     # zakat fitrah per jiwa
    "bulan_dalam_setahun": 12,    # untuk nisab bulanan zakat penghasilan
}


# ---------------------------------------------------------------------------
# FUNGSI BANTU
# ---------------------------------------------------------------------------
def cek_nisab(nilai, nisab):
    """Mengembalikan True jika nilai harta/penghasilan mencapai nisab."""
    return nilai >= nisab


def format_rupiah(angka):
    """Format angka menjadi 'Rp 1.234.567' (pemisah ribuan titik)."""
    return "Rp " + f"{angka:,.0f}".replace(",", ".")


def _ke_angka(nilai, nama_field):
    """Ubah input menjadi float; tolak teks, kosong, dan boolean."""
    if isinstance(nilai, bool) or nilai is None:
        raise ValueError(f"{nama_field} harus berupa angka.")
    try:
        return float(nilai)
    except (TypeError, ValueError):
        raise ValueError(f"{nama_field} harus berupa angka.")


def _angka_positif(nilai, nama_field):
    """Validasi angka > 0."""
    angka = _ke_angka(nilai, nama_field)
    if angka <= 0:
        raise ValueError(f"{nama_field} harus lebih besar dari 0.")
    return angka


# ---------------------------------------------------------------------------
# CLASS INDUK
# ---------------------------------------------------------------------------
class Zakat:
    """Class induk semua jenis zakat (dasar inheritance)."""

    jenis = "Zakat"

    def __init__(self, konfigurasi=None):
        self.konfigurasi = konfigurasi if konfigurasi else KONFIGURASI

    def _nisab_tahunan(self, harga_emas):
        """Nisab = 85 gram emas x harga emas per gram."""
        harga = _angka_positif(harga_emas, "Harga emas per gram")
        return self.konfigurasi["nisab_emas_gram"] * harga

    def _hasil(self, wajib, nisab, zakat, pesan):
        """Susun dictionary hasil sesuai kontrak tim."""
        return {
            "jenis": self.jenis,
            "wajib": wajib,
            "nisab": nisab,
            "zakat": zakat,
            "pesan": pesan,
        }

    def hitung(self, **kwargs):
        """Wajib ditimpa (override) oleh class turunan."""
        raise NotImplementedError("Method hitung() harus dibuat di class turunan.")


# ---------------------------------------------------------------------------
# CLASS TURUNAN
# ---------------------------------------------------------------------------
class ZakatPenghasilan(Zakat):
    """Zakat penghasilan: 2,5% jika penghasilan bulanan >= nisab bulanan."""

    jenis = "Zakat Penghasilan"

    def hitung(self, penghasilan_bulanan, harga_emas):
        penghasilan = _angka_positif(penghasilan_bulanan, "Penghasilan bulanan")
        nisab_bulanan = (
            self._nisab_tahunan(harga_emas) / self.konfigurasi["bulan_dalam_setahun"]
        )

        if cek_nisab(penghasilan, nisab_bulanan):
            zakat = penghasilan * self.konfigurasi["kadar_zakat"]
            pesan = (
                f"Penghasilan mencapai nisab bulanan ({format_rupiah(nisab_bulanan)}). "
                f"Zakat yang wajib dibayarkan: {format_rupiah(zakat)} per bulan."
            )
            return self._hasil(True, nisab_bulanan, zakat, pesan)

        pesan = (
            f"Penghasilan belum mencapai nisab bulanan ({format_rupiah(nisab_bulanan)}). "
            "Belum wajib zakat penghasilan."
        )
        return self._hasil(False, nisab_bulanan, 0, pesan)


class ZakatMal(Zakat):
    """Zakat mal: wajib jika harta >= nisab (85 gram emas) DAN haul 1 tahun."""

    jenis = "Zakat Mal"

    def hitung(self, total_harta, harga_emas, sudah_haul):
        harta = _angka_positif(total_harta, "Total harta")
        if not isinstance(sudah_haul, bool):
            raise ValueError("Status haul harus berupa Ya/Tidak.")
        nisab = self._nisab_tahunan(harga_emas)

        # percabangan bertingkat: nisab dulu, lalu haul
        if not cek_nisab(harta, nisab):
            pesan = (
                f"Harta belum mencapai nisab ({format_rupiah(nisab)}). "
                "Belum wajib zakat mal."
            )
            return self._hasil(False, nisab, 0, pesan)

        if not sudah_haul:
            pesan = (
                "Harta sudah mencapai nisab, tetapi belum dimiliki selama satu tahun "
                "(haul). Belum wajib zakat mal."
            )
            return self._hasil(False, nisab, 0, pesan)

        zakat = harta * self.konfigurasi["kadar_zakat"]
        pesan = (
            f"Harta mencapai nisab ({format_rupiah(nisab)}) dan sudah haul. "
            f"Zakat mal yang wajib dibayarkan: {format_rupiah(zakat)}."
        )
        return self._hasil(True, nisab, zakat, pesan)


class ZakatFitrah(Zakat):
    """Zakat fitrah: 2,5 kg beras per jiwa x harga beras per kg."""

    jenis = "Zakat Fitrah"

    def hitung(self, jumlah_jiwa, harga_beras):
        # jumlah jiwa harus bilangan bulat positif
        angka_jiwa = _angka_positif(jumlah_jiwa, "Jumlah jiwa")
        if angka_jiwa != int(angka_jiwa):
            raise ValueError("Jumlah jiwa harus bilangan bulat.")
        jiwa = int(angka_jiwa)
        harga = _angka_positif(harga_beras, "Harga beras per kg")

        beras_kg = self.konfigurasi["beras_per_jiwa_kg"] * jiwa
        zakat = beras_kg * harga
        pesan = (
            f"Zakat fitrah untuk {jiwa} jiwa = {beras_kg:g} kg beras. "
            f"Jika dibayar dengan uang: {format_rupiah(zakat)}."
        )
        # zakat fitrah tidak memakai nisab harta -> nisab = 0
        return self._hasil(True, 0, zakat, pesan)


# ---------------------------------------------------------------------------
# PENCATAT INFAQ
# ---------------------------------------------------------------------------
class PencatatInfaq:
    """Menyimpan transaksi infaq (selama sesi) dan merekapnya per pekan."""

    def __init__(self):
        self.transaksi = []  # list of dict: tanggal, donatur, jumlah

    @staticmethod
    def _validasi_tanggal(tanggal):
        """Terima objek date/datetime atau teks 'YYYY-MM-DD'."""
        if isinstance(tanggal, datetime):
            return tanggal.date()
        if isinstance(tanggal, date):
            return tanggal
        if isinstance(tanggal, str):
            try:
                return datetime.strptime(tanggal.strip(), "%Y-%m-%d").date()
            except ValueError:
                pass
        raise ValueError("Tanggal tidak valid. Gunakan format YYYY-MM-DD.")

    def catat(self, tanggal, nama_donatur, jumlah):
        """Validasi lalu simpan satu transaksi infaq. Mengembalikan transaksi itu."""
        tgl = self._validasi_tanggal(tanggal)

        if not isinstance(nama_donatur, str) or not nama_donatur.strip():
            raise ValueError("Nama donatur tidak boleh kosong.")

        nominal = _angka_positif(jumlah, "Jumlah infaq")

        data = {
            "tanggal": tgl,
            "donatur": nama_donatur.strip(),
            "jumlah": nominal,
        }
        self.transaksi.append(data)
        return data

    @staticmethod
    def _label_pekan(tgl):
        """Label pekan ISO, contoh: '2026-W47'."""
        tahun, pekan, _ = tgl.isocalendar()
        return f"{tahun}-W{pekan:02d}"

    def rekap_per_pekan(self):
        """Jumlahkan infaq per pekan. Mengembalikan dict {label_pekan: total}."""
        rekap = {}
        for t in self.transaksi:
            label = self._label_pekan(t["tanggal"])
            rekap[label] = rekap.get(label, 0) + t["jumlah"]
        return dict(sorted(rekap.items()))

    def total_keseluruhan(self):
        """Total semua infaq yang tercatat."""
        total = 0
        for t in self.transaksi:
            total += t["jumlah"]
        return total

    def hapus_semua(self):
        """Kosongkan data (misalnya tombol reset di antarmuka)."""
        self.transaksi.clear()


# ---------------------------------------------------------------------------
# Uji cepat: jalankan `python logika.py`
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    harga_emas = 1_500_000  # contoh saja, ganti sesuai rilis BAZNAS

    print(ZakatPenghasilan().hitung(10_000_000, harga_emas)["pesan"])
    print(ZakatMal().hitung(200_000_000, harga_emas, True)["pesan"])
    print(ZakatFitrah().hitung(4, 15_000)["pesan"])

    infaq = PencatatInfaq()
    infaq.catat("2026-11-16", "Hamba Allah", 50_000)
    infaq.catat("2026-11-18", "Pak Budi", 100_000)
    infaq.catat("2026-11-24", "Bu Siti", 75_000)
    print(infaq.rekap_per_pekan(), format_rupiah(infaq.total_keseluruhan()))
