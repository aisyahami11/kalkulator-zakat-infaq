"""
test_logika.py - Kasus uji untuk logika.py
Peran 4: Penguji dan Dokumentasi

Jalankan:  python -m unittest test_logika -v
"""

import unittest

from logika import (
    PencatatInfaq,
    ZakatFitrah,
    ZakatMal,
    ZakatPenghasilan,
    cek_nisab,
)

HARGA_EMAS = 1_500_000  # contoh; nisab tahunan = 127.500.000, bulanan = 10.625.000
KUNCI = {"jenis", "wajib", "nisab", "zakat", "pesan"}


class TestCekNisab(unittest.TestCase):
    def test_sama_dengan_nisab_dianggap_mencapai(self):
        self.assertTrue(cek_nisab(100, 100))

    def test_di_bawah_nisab(self):
        self.assertFalse(cek_nisab(99, 100))


class TestZakatPenghasilan(unittest.TestCase):
    def test_mencapai_nisab(self):
        h = ZakatPenghasilan().hitung(12_000_000, HARGA_EMAS)
        self.assertEqual(set(h), KUNCI)
        self.assertTrue(h["wajib"])
        self.assertAlmostEqual(h["zakat"], 300_000)

    def test_belum_nisab(self):
        h = ZakatPenghasilan().hitung(5_000_000, HARGA_EMAS)
        self.assertFalse(h["wajib"])
        self.assertEqual(h["zakat"], 0)

    def test_input_salah(self):
        for salah in ["abc", "", None, -1, 0, True]:
            with self.subTest(salah=salah):
                with self.assertRaises(ValueError):
                    ZakatPenghasilan().hitung(salah, HARGA_EMAS)

    def test_harga_emas_salah(self):
        with self.assertRaises(ValueError):
            ZakatPenghasilan().hitung(10_000_000, 0)


class TestZakatMal(unittest.TestCase):
    def test_wajib(self):
        h = ZakatMal().hitung(200_000_000, HARGA_EMAS, True)
        self.assertTrue(h["wajib"])
        self.assertAlmostEqual(h["zakat"], 5_000_000)

    def test_belum_nisab(self):
        self.assertFalse(ZakatMal().hitung(100_000_000, HARGA_EMAS, True)["wajib"])

    def test_belum_haul(self):
        h = ZakatMal().hitung(200_000_000, HARGA_EMAS, False)
        self.assertFalse(h["wajib"])
        self.assertEqual(h["zakat"], 0)

    def test_input_salah(self):
        with self.assertRaises(ValueError):
            ZakatMal().hitung("banyak", HARGA_EMAS, True)
        with self.assertRaises(ValueError):
            ZakatMal().hitung(200_000_000, HARGA_EMAS, "ya")


class TestZakatFitrah(unittest.TestCase):
    def test_hitung(self):
        h = ZakatFitrah().hitung(4, 15_000)
        self.assertTrue(h["wajib"])
        self.assertAlmostEqual(h["zakat"], 150_000)

    def test_input_salah(self):
        for jiwa, beras in [(0, 15_000), (-2, 15_000), (2.5, 15_000), ("x", 15_000), (3, 0), (3, "mahal")]:
            with self.subTest(jiwa=jiwa, beras=beras):
                with self.assertRaises(ValueError):
                    ZakatFitrah().hitung(jiwa, beras)


class TestPencatatInfaq(unittest.TestCase):
    def setUp(self):
        self.p = PencatatInfaq()

    def test_catat_dan_rekap(self):
        self.p.catat("2026-11-16", "A", 50_000)
        self.p.catat("2026-11-18", "B", 100_000)
        self.p.catat("2026-11-24", "C", 75_000)
        rekap = self.p.rekap_per_pekan()
        self.assertEqual(rekap, {"2026-W47": 150_000, "2026-W48": 75_000})
        self.assertEqual(self.p.total_keseluruhan(), 225_000)

    def test_input_salah_tidak_tersimpan(self):
        salah = [
            ("32-13-2026", "A", 1000),
            ("2026-11-20", "   ", 1000),
            ("2026-11-20", "A", 0),
            ("2026-11-20", "A", -5),
            ("2026-11-20", "A", "abc"),
            ("2026-11-20", "A", None),
        ]
        for data in salah:
            with self.subTest(data=data):
                with self.assertRaises(ValueError):
                    self.p.catat(*data)
        self.assertEqual(self.p.transaksi, [])

    def test_rekap_kosong(self):
        self.assertEqual(self.p.rekap_per_pekan(), {})
        self.assertEqual(self.p.total_keseluruhan(), 0)


if __name__ == "__main__":
    unittest.main()
