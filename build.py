from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image,
                                KeepTogether, PageBreak, Flowable)
from PIL import Image as PI
import os

D = os.path.dirname(os.path.abspath(__file__))
S = os.path.join(D, "shots")
NAVY = colors.HexColor("#12394d")
LIGHT = colors.HexColor("#e9f1f4")

base = ParagraphStyle("b", fontName="Helvetica", fontSize=8.6, leading=11.2, spaceAfter=3)
small = ParagraphStyle("s", parent=base, fontSize=7.6, leading=9.6)
cap = ParagraphStyle("c", parent=base, fontSize=7.8, leading=10, textColor=colors.HexColor("#333333"), spaceAfter=5)
cell = ParagraphStyle("cell", parent=base, fontSize=7.8, leading=9.6, spaceAfter=0)
cellb = ParagraphStyle("cellb", parent=cell, fontName="Helvetica-Bold")
cellh = ParagraphStyle("cellh", parent=cell, fontName="Helvetica-Bold", textColor=colors.white)
h1 = ParagraphStyle("h1", parent=base, fontName="Helvetica-Bold", fontSize=12, leading=15, textColor=NAVY, spaceBefore=4, spaceAfter=4)
title = ParagraphStyle("t", parent=base, fontName="Helvetica-Bold", fontSize=15, leading=18, textColor=NAVY, spaceAfter=2)
mono = ParagraphStyle("m", parent=base, fontName="Courier", fontSize=7.6, leading=9.4)

P = lambda t, s=base: Paragraph(t, s)


def table(rows, widths, header=True, bold_first=False):
    data = []
    for i, r in enumerate(rows):
        st = cellh if (header and i == 0) else (cellb if bold_first and True else cell)
        data.append([Paragraph(str(c), cellb if (bold_first and j == 0 and i > 0) else st) for j, c in enumerate(r)])
    t = Table(data, colWidths=[w * cm for w in widths], repeatRows=1 if header else 0)
    sty = [("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#b8c7ce")),
           ("VALIGN", (0, 0), (-1, -1), "TOP"),
           ("LEFTPADDING", (0, 0), (-1, -1), 3), ("RIGHTPADDING", (0, 0), (-1, -1), 3),
           ("TOPPADDING", (0, 0), (-1, -1), 2), ("BOTTOMPADDING", (0, 0), (-1, -1), 2)]
    if header:
        sty.append(("BACKGROUND", (0, 0), (-1, 0), NAVY))
    for i in range(1, len(rows), 2):
        sty.append(("BACKGROUND", (0, i), (-1, i), LIGHT))
    t.setStyle(TableStyle(sty))
    return t


def shot(name, width_cm, caption, crop=None):
    p = os.path.join(S, name)
    if crop:
        im = PI.open(p).crop(crop)
        p = os.path.join(S, "crop_" + name)
        im.save(p)
    w, h = PI.open(p).size
    img = Image(p, width=width_cm * cm, height=width_cm * cm * h / w)
    img.hAlign = "LEFT"
    return KeepTogether([img, P(caption, cap)])


class Diagram(Flowable):
    W, H = 17.4 * cm, 6.3 * cm

    def wrap(self, *a):
        return self.W, self.H

    def box(self, c, x, y, w, h, text, fill=None, dash=False, bold=False):
        c.saveState()
        if dash:
            c.setDash(3, 2)
        c.setStrokeColor(NAVY)
        c.setLineWidth(1)
        if fill:
            c.setFillColor(fill)
        c.roundRect(x, y, w, h, 4, stroke=1, fill=1 if fill else 0)
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold" if bold else "Helvetica", 7.2)
        lines = text.split("\n")
        ty = y + h / 2 + (len(lines) - 1) * 4.2 - 2.5
        for i, l in enumerate(lines):
            c.drawCentredString(x + w / 2, ty - i * 8.4, l)
        c.restoreState()

    def arrow(self, c, x1, y1, x2, y2, label="", dash=False, lx=0, ly=3):
        c.saveState()
        c.setStrokeColor(NAVY)
        c.setFillColor(NAVY)
        if dash:
            c.setDash(3, 2)
        c.line(x1, y1, x2, y2)
        c.setDash()
        import math
        ang = math.atan2(y2 - y1, x2 - x1)
        p = c.beginPath()
        p.moveTo(x2, y2)
        for da in (math.pi - 0.45, math.pi + 0.45):
            p.lineTo(x2 + 6 * math.cos(ang + da), y2 + 6 * math.sin(ang + da))
        p.close()
        c.drawPath(p, fill=1, stroke=0)
        if label:
            c.setFont("Helvetica-Oblique", 6.6)
            c.setFillColor(colors.black)
            for i, l in enumerate(label.split("\n")):
                c.drawCentredString((x1 + x2) / 2 + lx, max(y1, y2) + ly + (len(label.split("\n")) - 1 - i) * 7, l)
        c.restoreState()

    def draw(self):
        c = self.canv
        cm_ = cm
        self.box(c, 0, 2.3 * cm_, 3.3 * cm_, 1.9 * cm_, "SUMBER DATA\nNASA FIRMS VIIRS\nsea_fires_7d.csv", fill=colors.HexColor("#fff3d6"), bold=True)
        self.box(c, 4.3 * cm_, 2.3 * cm_, 2.7 * cm_, 1.9 * cm_, "Ingestion\n(NiFi/Kafka)\nbelum ada", dash=True)
        self.box(c, 8.0 * cm_, 1.7 * cm_, 4.6 * cm_, 3.1 * cm_,
                 "HBase 2.6.7 (standalone)\nTabel: hotspot\nCF loc: lat, lon\nCF sensor: frp, conf\nrow key: grid#tgl-terbalik#jam#urut",
                 fill=colors.HexColor("#d9ecf2"), bold=True)
        self.box(c, 13.6 * cm_, 3.9 * cm_, 3.6 * cm_, 1.6 * cm_, "Serving (API peta)\nbelum ada", dash=True)
        self.box(c, 13.6 * cm_, 1.9 * cm_, 3.6 * cm_, 1.6 * cm_, "Processing Spark/Hive\n(Topic 10) belum ada", dash=True)
        self.box(c, 13.6 * cm_, 0.0 * cm_, 3.6 * cm_, 1.5 * cm_, "Visualisasi / dashboard\nbelum ada", dash=True)
        y = 3.25 * cm_
        self.arrow(c, 3.3 * cm_, y, 4.3 * cm_, y, "CSV", dash=True)
        self.arrow(c, 7.0 * cm_, y, 8.0 * cm_, y, "baris\ntitik api", dash=True, lx=0)
        self.arrow(c, 12.6 * cm_, 4.1 * cm_, 13.6 * cm_, 4.7 * cm_, "get/scan", lx=0, ly=2)
        self.arrow(c, 12.6 * cm_, 2.7 * cm_, 13.6 * cm_, 2.7 * cm_, "ekspor\nbatch", dash=True)
        self.arrow(c, 15.4 * cm_, 1.9 * cm_, 15.4 * cm_, 1.5 * cm_, "", dash=True)
        c.setFont("Helvetica-Oblique", 7)
        c.drawString(0, 0.5 * cm_, "Garis penuh = sudah dibangun & diuji (Topic 9). Kotak putus-putus = lapisan yang ditambahkan di Topic 10-12.")


def footer(c, d):
    c.saveState()
    c.setFont("Helvetica", 7.5)
    c.setFillColor(colors.grey)
    c.drawString(1.6 * cm, 0.9 * cm, "Teknologi Big Data - Topic 9 - Kelompok 6")
    c.drawRightString(A4[0] - 1.6 * cm, 0.9 * cm, "Halaman %d" % d.page)
    c.restoreState()


doc = SimpleDocTemplate(os.path.join(D, "Tugas_Topic09_HBase_Kelompok6.pdf"), pagesize=A4,
                        leftMargin=1.6 * cm, rightMargin=1.6 * cm, topMargin=1.4 * cm, bottomMargin=1.5 * cm,
                        title="Tugas Topic 9 - Case Study Brief dan Desain Storage HBase", author="Kelompok 6")
E = []

# ---------------- Bab 1 ----------------
E += [P("Case Study Brief dan Desain Storage HBase: Pemantauan Titik Api Indonesia", title),
      P("Teknologi Big Data - Topic 9 - Tugas Kelompok", small),
      table([["Kelompok 6", "NPM", "Pembagian tugas"],
             ["Muhammad Bryan Farras", "2306230975", "Bab 1 (case study, 4V, pertanyaan data) dan Bab 4 (perbandingan)"],
             ["Mirza Adi Raffiansyah", "2306210323", "Bab 2 (skema, 5 baris contoh, uji hotspot)"],
             ["Calvin Wirathama Katoroy", "2306242395", "Bab 3 (instalasi HBase, hands-on, screenshot, uji waktu)"],
             ["Salim", "2306204604", "Bab 5 (Catatan Keputusan Desain), diagram v0.1, penyusunan PDF"]], [5, 2.6, 9.8]),
      Spacer(1, 4),
      P("Bab 1. Case Study Brief", h1),
      P("<b>Kasus.</b> Sistem pemantauan titik api (hotspot) kebakaran hutan dan lahan di Indonesia. Sumbernya adalah deteksi "
        "satelit VIIRS NASA FIRMS (latitude, longitude, waktu deteksi, FRP, confidence). Kasus yang sama dipakai pada tugas MapReduce "
        "kelompok (dataset <i>sea_fires_7d.csv</i>, 19-25 September 2026), sehingga seluruh angka di bawah dihitung dari data tersebut. "
        "Pengguna sistem adalah petugas pemantau yang membuka peta per wilayah dan melihat titik api terbaru."),
      table([["V", "Angka dan alasan (dihitung dari data kelompok)"],
             ["Volume", "Sampel 7 hari: 64.389 baris se-Asia Tenggara, 54.516 baris di kotak Indonesia (lat -11..6, lon 95..141), file 5,3 MB (+-82 byte/baris). "
                        "Rata-rata 7.788 titik/hari, setara +-2,8 juta/tahun. <i>Asumsi:</i> 3 sensor VIIRS dan arsip 10 tahun, sehingga +-85 juta baris (+-7 GB CSV; "
                        "+-20-30 GB di HBase karena row key diulang pada tiap sel)."],
             ["Velocity", "Rata-rata hanya 0,09 titik/detik, tetapi datang berkelompok per lintasan satelit. <i>Asumsi:</i> +-4 unggahan efektif per hari, +-2.000 baris tiap unggahan. "
                          "Ada lonjakan musim kemarau: 10.974 titik pada 19 Sep melawan 5.686 pada 25 Sep (hampir 2 kali lipat dalam 6 hari)."],
             ["Variety", "CSV terstruktur (13 kolom: koordinat, waktu, brightness, FRP, confidence, day/night). Dapat bertambah dengan data semi-terstruktur (GeoJSON batas wilayah, cuaca) "
                         "dan laporan teks warga. Satelit berbeda memberi kolom yang berbeda."],
             ["Veracity", "Confidence: nominal 91,9% (50.095), low 4,3% (2.331), high 3,8% (2.090). FRP berkisar 0,17-824,73 MW (rata-rata 7,45), jadi ada pencilan ekstrem. "
                          "Kotak lat/lon kasar ikut menangkap sebagian Malaysia, Papua Nugini, dan Timor Leste; 0 duplikat persis pada sampel. Titik confidence low perlu ditandai, bukan dibuang."]],
            [2.2, 15.2], bold_first=True),
      Spacer(1, 5),
      P("<b>Pertanyaan data</b> (sel grid = kotak 1 derajat x 1 derajat, ada 300 sel berisi titik pada sampel)", base),
      table([["No", "Pertanyaan", "Jenis akses", "Seberapa sering", "Dijawab oleh"],
             ["1", "Tampilkan 20 titik api terbaru pada sel grid X (peta wilayah)", "Scan rentang sempit", "Setiap peta dibuka", "<b>HBase</b>"],
             ["2", "Tampilkan detail satu titik api (klik pada peta)", "Lookup per key (get)", "Puluhan kali per menit", "<b>HBase</b>"],
             ["3", "Titik api pada sel X dalam N hari terakhir", "Scan rentang sempit", "Beberapa kali per menit", "<b>HBase</b>"],
             ["4", "Titik api confidence <i>high</i> dengan FRP &gt; 50 MW untuk peringatan", "Filter lintas sel", "Tiap jam", "Spark (Topic 10)"],
             ["5", "Jumlah titik api per provinsi per hari dan tren harian", "Agregasi", "Sekali sehari", "Hive/Spark (Topic 10)"]],
            [0.8, 7.2, 3.2, 3.2, 3.0]),
      PageBreak()]

# ---------------- Bab 2 ----------------
E += [P("Bab 2. Desain Skema HBase", h1),
      P("<b>Tabel</b> <font face='Courier'>hotspot</font> dengan dua column family. <b>Row key</b> = "
        "<font face='Courier'>grid#tanggal_terbalik#jam#urut</font>, contoh <font face='Courier'>g087112#79739075#0533#43856</font>. "
        "<font face='Courier'>grid</font> = <font face='Courier'>g</font> + (floor(lat)+90, 3 digit) + floor(lon) (3 digit), jadi <i>g087112</i> adalah lat -3..-2, lon 112..113 (Kalimantan Tengah). "
        "<font face='Courier'>tanggal_terbalik</font> = 99999999 - yyyymmdd, sehingga titik api terbaru terurut paling depan dan pertanyaan 1 dan 3 cukup satu scan dari awal awalan grid. "
        "<font face='Courier'>urut</font> menjamin key unik bila dua titik terdeteksi pada jam yang sama."),
      P("<b>Column family.</b> <font face='Courier'>loc</font> (lat, lon: dibaca untuk menggambar peta) dan <font face='Courier'>sensor</font> (frp, conf: dibaca untuk detail dan penyaringan). "
        "Dua family sudah cukup (anjuran 1-3), dan data yang jarang dipakai dapat dipisah tanpa menambah family. Qualifier boleh berbeda antar baris; "
        "sensor lain (mis. MODIS) dapat menambah kolom <font face='Courier'>sensor:brightness</font> tanpa mengubah skema."),
      P("<b>5 baris contoh</b> (diambil dari data nyata, dimuat pada Bab 3):", base),
      table([["Row key", "loc:lat", "loc:lon", "sensor:frp", "sensor:conf"],
             ["g085122#79739076#0553#36563", "-4.39419", "122.66214", "5.83", "nominal"],
             ["g086111#79739078#0631#23462", "-3.47306", "111.92799", "5.28", "nominal"],
             ["g087111#79739080#0527#02562", "-2.50477", "111.5566", "63.86", "high"],
             ["g087113#79739075#1815#46688", "-2.13067", "113.78811", "4.37", "nominal"],
             ["g087114#79739079#1749#18605", "-2.70884", "114.07139", "2.23", "nominal"]],
            [5.6, 2.6, 2.8, 2.6, 3.8]),
      Spacer(1, 5),
      P("<b>Uji hotspot di atas kertas</b> (1.000 tulisan baru per detik)", h1),
      P("<b>(a) Apakah key baru berawalan sama atau berurutan?</b> Tidak. Awalan adalah grid, dan titik api baru muncul di banyak sel sekaligus (300 sel berisi titik pada sampel 7 hari), sehingga tulisan menyebar ke banyak region. "
        "Tanggal berada setelah grid, jadi waktu tidak membuat key menumpuk di ujung tabel. Tabel tetap perlu di-<i>pre-split</i> menurut awalan grid agar tidak mulai dari satu region."),
      P("<b>(b) Jika 80% trafik menuju satu key/sel?</b> Satu RegionServer menjadi hotspot; ini mungkin terjadi karena sel g087112 sendiri sudah memegang 5.107 dari 54.516 titik (9,4%). "
        "Pengurangannya: pecah sel panas menjadi 0,25 derajat dan tambah awalan <i>salt</i> (urut mod 4) pada sel panas saja. Konsekuensinya, tulisan lebih menyebar tetapi scan satu sel menjadi 4 scan kecil yang digabung di klien."),
      P("<b>(c) Apakah pertanyaan paling sering masih satu get/scan sempit?</b> Ya, pertanyaan 1-3 tetap satu <font face='Courier'>get</font> atau satu <font face='Courier'>scan</font> STARTROW/STOPROW pada satu awalan grid (Bab 3: 925 baris sel g087112 terbaca tanpa memindai 9.075 baris lain). "
        "Kelemahannya, viewport peta yang menyeberang batas sel butuh beberapa scan, dan pertanyaan 4-5 memang tidak efisien di HBase."),
      PageBreak()]

# ---------------- Bab 3 ----------------
E += [P("Bab 3. Bukti Hands-on", h1),
      P("<b>Lingkungan.</b> Windows 11 + WSL2, Ubuntu 24.04 LTS, OpenJDK 17.0.20.1, Apache HBase 2.6.7 (hadoop3-bin), mode standalone. "
        "Data disimpan di <font face='Courier'>/root/hbase-data</font> (bukan /tmp). Catatan: karena nama host WSL membuat RegionServer gagal mendaftar ke Master, "
        "ditambahkan <font face='Courier'>hbase.master.hostname</font> dan <font face='Courier'>hbase.regionserver.hostname</font> = 127.0.0.1 di hbase-site.xml. "
        "<b>Batasan:</b> standalone = master, RegionServer, dan ZooKeeper dalam satu proses di satu mesin, sehingga tidak mencerminkan replikasi, failover, atau pembagian region antar server."),
      shot("01_env.png", 12.5, "<b>Gambar 1.</b> java -version, jps (HMaster berjalan), dan hbase version 2.6.7. Menjawab: lingkungan dan instalasi berjalan."),
      shot("02_webui.png", 9.0, "<b>Gambar 2.</b> Antarmuka web http://localhost:16010: satu RegionServer Normal, versi 2.6.7-hadoop3, tabel hotspot terdaftar. Menjawab: Master dan RegionServer hidup.",
           crop=(0, 0, 1280, 1000)),
      shot("03_create.png", 13.0, "<b>Gambar 3.</b> <font face='Courier'>create 'hotspot','loc','sensor'</font>, list, dan describe. Menjawab: skema dua family dari Bab 2 sudah terbentuk dan ENABLED."),
      shot("04_put.png", 12.0, "<b>Gambar 4.</b> put untuk lima baris contoh Bab 2 (4 kolom per baris; tampak 17 put pertama, sisanya sama pola). Menjawab: data titik api nyata masuk ke key yang dirancang."),
      shot("05_get.png", 14.5, "<b>Gambar 5.</b> <font face='Courier'>get</font> satu row key. Menjawab pertanyaan 2: detail satu titik api per klik (0,44 detik adalah panggilan pertama, saat belum ada cache)."),
      shot("06_scan_rentang.png", 14.5, "<b>Gambar 6.</b> scan STARTROW 'g087112#' STOPROW 'g087112$' LIMIT 3. Menjawab pertanyaan 1 dan 3: titik api pada satu sel grid, berurutan dari yang terbaru, tanpa membaca sel lain."),
      shot("07_waktu.png", 11.0, "<b>Gambar 7.</b> Setelah 10.000 baris titik api nyata dimuat (+-24 detik): count, get, scan rentang, dan scan dengan ValueFilter. Menjawab: biaya tiap pola akses."),
      table([["Perintah (10.000 baris)", "Baris diproses", "Baris dikembalikan", "Waktu (shell)"],
             ["get satu row key", "1", "1", "0,0733 detik"],
             ["scan rentang sel g087112 (tanpa LIMIT)", "925", "925 (3.700 sel)", "0,9666 detik"],
             ["scan ValueFilter(=, 'binary:63.86')", "10.000 (semua)", "1", "0,1067 detik"]],
            [7.4, 3.2, 3.6, 3.2]),
      Spacer(1, 3),
      P("<b>Kesimpulan.</b> <b>get</b> adalah yang tercepat karena key langsung menunjuk ke satu baris dan biayanya tidak ikut naik bila tabel membesar. "
        "Scan rentang 0,97 detik terlihat lebih lambat bukan karena membaca banyak, melainkan karena mengembalikan dan mencetak 925 baris (LIMIT 3 pada Gambar 6 hampir instan). "
        "Filter harus memeriksa seluruh 10.000 baris; pada ukuran ini masih cepat (0,107 detik) karena tabel kecil dan sudah di memori, tetapi biayanya tumbuh linear dengan ukuran tabel, "
        "sedangkan get dan scan sempit tidak. Waktu hanya dari satu kali jalan di laptop kami; yang dinilai adalah pola, bukan angka mutlak."),
      ]

# ---------------- Bab 4 ----------------
E += [P("Bab 4. Perbandingan HBase dengan PostgreSQL/PostGIS", h1),
      table([["Kriteria", "HBase", "PostgreSQL (+PostGIS)"],
             ["Pola akses utama", "Get dan scan per sel grid + waktu: row key membuatnya satu scan sempit (Gambar 6, 925 baris dari 10.000).",
              "Cepat dengan indeks spasial/B-tree, tetapi indeks harus dirawat dan melambat bila tabel berisi puluhan sampai ratusan juta baris."],
             ["Skala tulis", "Unggahan berkelompok per lintasan (+-2.000 baris), arsip 85 juta baris; tulis menyebar antar region dan tambah mesin untuk skala.",
              "Satu server utama menerima tulis; pada 85 juta baris + indeks, perawatan (vacuum, reindex) makin berat."],
             ["Join dan agregasi", "Tidak ada. Pertanyaan 4-5 (per provinsi, tren harian) harus lewat Spark/Hive.", "Kuat: GROUP BY dan join ke tabel provinsi langsung dengan SQL."],
             ["Skema", "Luwes: sensor baru menambah qualifier tanpa migrasi.", "Kaku: kolom baru per sensor butuh ALTER TABLE atau banyak NULL."],
             ["Transaksi", "Konsisten per baris; data titik api tulis-sekali, jadi cukup.", "ACID penuh; tidak terpakai pada data deteksi yang tidak diubah."],
             ["Operasional", "Berat (ZooKeeper, HMaster, RegionServer, idealnya HDFS); di sini hanya standalone.", "Ringan dan dikenal luas."],
             ["Kesimpulan kasus ini", "Dipilih untuk penyimpanan event titik api.", "Dipakai untuk data referensi (batas provinsi, akun pengguna)."]],
            [3.0, 7.2, 7.2], bold_first=True),
      Spacer(1, 3),
      P("<b>Kriteria paling menentukan:</b> pola akses dan skala tulis. Pertanyaan yang paling sering diajukan (1-3) semuanya berbentuk \"satu sel grid pada rentang waktu\", "
        "yang dapat dibuat menjadi satu scan sempit hanya dengan merancang row key; data juga hanya bertambah dan tidak diubah. Kelemahan terbesar HBase yaitu tidak ada join dan agregasi "
        "kami terima, karena pertanyaan 4-5 jarang (jam-an dan harian) dan akan dikerjakan di lapisan processing (Topic 10)."),
      P("Bab 5. Catatan Keputusan Desain dan Diagram Arsitektur v0.1", h1),
      table([["Bagian", "Isi"],
             ["Keputusan", "Event titik api (VIIRS) Indonesia disimpan di HBase, tabel <i>hotspot</i>, row key grid#tanggal-terbalik#jam#urut, family loc dan sensor."],
             ["Konteks", "Sampel kami: 54.516 titik/7 hari (+-2,8 juta/tahun), proyeksi +-85 juta baris. Pengguna membuka peta per sel dan butuh 20 titik terbaru pada satu sel dalam waktu "
                         "kurang dari 1 detik (terukur 0,07 detik untuk get dan 0,97 detik untuk scan 925 baris). Tulis datang berkelompok dengan lonjakan musim kemarau (10.974 titik/hari pada puncak sampel)."],
             ["Alternatif ditolak", "<b>PostgreSQL/PostGIS</b> sebagai penyimpan event: tulis terpusat di satu server dan indeks membengkak pada puluhan juta baris; hanya dipakai untuk data referensi. "
                                    "<b>Hive</b>: bagus untuk agregasi harian tetapi tidak cocok untuk lookup berlatensi rendah per key."],
             ["Konsekuensi", "Tidak ada join dan agregasi bawaan: laporan per provinsi dan tren dikerjakan di Spark/Hive. Row key tetap setelah dibuat; "
                             "query berdasar provinsi atau confidence saja menjadi scan penuh (butuh tabel indeks sendiri). Sel panas (g087112 = 9,4% data) perlu pre-split dan salt; "
                             "viewport lintas sel butuh beberapa scan. Standalone belum menguji replikasi dan failover; operasional HBase lebih berat daripada PostgreSQL."],
             ["Bukti", "Gambar 3 (skema), 4 (put), 5 (get 1 baris), 6 (scan sel g087112), 7 (get 0,073 detik, scan 925 baris 0,97 detik, filter penuh 0,107 detik pada 10.000 baris)."]],
            [3.0, 14.4], bold_first=True),
      Spacer(1, 4),
      KeepTogether([P("<b>Diagram arsitektur v0.1</b>", base), Diagram()])]

doc.build(E, onFirstPage=footer, onLaterPages=footer)
print("ok")
