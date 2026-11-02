# Topic 9 – Apache HBase (Kelompok 6)

Tugas kelompok mata kuliah **Teknologi Big Data**: merancang dan membuktikan model data HBase untuk studi kasus **titik api (hotspot) di Indonesia**, memakai data NASA FIRMS VIIRS (19–25 Sep 2026, ±54 ribu baris untuk wilayah Indonesia).

## Ringkasan

| | |
|---|---|
| Kasus | Titik api VIIRS – 4V, 5 pertanyaan data |
| Skema | Row key `grid#tanggal-terbalik#jam#id`, column family `loc` dan `sensor`; uji hotspot dan pre-split |
| Lingkungan | HBase 2.6.7 standalone, OpenJDK 17, Ubuntu 24.04 di WSL2 |
| Bukti | 7 screenshot asli (terminal + Web UI), uji waktu get / range scan / filter pada 10.000 baris |
| Pembanding | PostgreSQL/PostGIS |
| Keputusan | Catatan Keputusan Desain (5 bagian) + diagram arsitektur v0.1 |

## Struktur repo

```
report/            laporan final
  Tugas_Topic09_HBase_Kelompok6.pdf    <- yang dikumpulkan (5 halaman)
  Tugas_Topic09_HBase_Kelompok6.docx   versi Word (gambar tertanam)
  Tugas_Topic09_HBase_Kelompok6.md     versi Markdown
  build.py                             pembuat PDF (reportlab)
  shots/                               7 screenshot + diagram arsitektur
hbase/             skrip yang dijalankan di HBase shell
  s3.rb  create table      s4.rb  put 5 baris contoh
  s5g.rb get               s6r.rb range scan
  s7.rb  count/get/scan/filter   load10k.rb  muat 10.000 baris
  run.sh                   jalankan skrip → hbase/output/*.out
  output/                  keluaran mentah tiap langkah
tools/
  cap.ps1                  screenshot jendela terminal asli (Windows)
```

## Menjalankan ulang

Di WSL (HBase sudah terpasang dan menyala):

```bash
HBASE_HOME=/root/hbase-2.6.7-hadoop3 ./hbase/run.sh s3 s4 s5g s7
```

Membangun ulang PDF:

```bash
pip install reportlab
python report/build.py
```

## Anggota

| Nama | Bagian |
|---|---|
| Bryan | Bab 1 (studi kasus, 4V, pertanyaan data), Bab 4 (perbandingan) |
| Mirza | Bab 2 (skema, 5 baris contoh, uji hotspot) |
| Calvin | Bab 3 (instalasi, hands-on, screenshot, uji waktu) |
| Salim | Bab 5 (Catatan Keputusan Desain), diagram v0.1, penyusunan PDF |

Nama lengkap dan NPM ada di halaman 1 laporan.
