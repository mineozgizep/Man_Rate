from flask import Flask, render_template, request, redirect, url_for
import pymysql

import os
import random

from db_config import get_db_connection


app = Flask(__name__)

# SORU METİNLERİ
sorular = {
    "Empati": "Duyguların radarında mı, yoksa sadece Netflix’in duygusal sahnelerinde mi ağlıyor?",
    "Güvenilirlik": "Sözünde durur mu, yoksa ‘seni ararım’ dediği gibi 3 gün sonra mı hatırlar?",
    "Duygusallık": "Gül yaprağında gözyaşı mı var, yoksa sadece soğuk esprilerle mi yaşıyor?",
    "Romantiklik": "Sürpriz çiçekler mi gönderir, yoksa özel günleri Google Takvim’den mi öğrenir?",
    "Espri Anlayışı": "Kahkahalarla mı güldürür, yoksa espri yaptığı açıklama gerektirir mi?",
    "Zeka": "Sözleriyle etkiler mi, yoksa bulmaca çözerken bile yardım ister mi?",
    "Hırs": "Hedeflerine koşar mı, yoksa motivasyonu ‘yarın başlarım’ mı?",
    "Tutku": "Gözleriyle yakar mı, yoksa ilgisi yalnızca telefon ekranına mı?",
    "Sorumluluk": "Planlara sadık mı, yoksa ‘Unuttum yaa’ onun ikinci adı mı?",
    "Dürüstlük": "Gerçekleri mi söyler, yoksa doğruyu biraz süsleyerek mi anlatır?",
    "Kıskançlık": "Tatlı bir sahiplenme mi, yoksa FBI moduna geçen biri mi?",
    "Sosyal Hayat": "Çevresiyle dengede mi, yoksa ya ev kuşu ya da sosyal kelebek mi?",
    "Seyahat Macera": "Uçağa atlayıp kaçmak mı ister, yoksa valizi bile görünce yorulur mu?",
    "Fiziksel Çekicilik": "Bakışlarıyla büyüler mi, yoksa tarzı ‘evden alelacele çıktım’ mı?",
    "Cinsel Uyum": "Birlikte ritmi yakalar mısınız, yoksa biri rock diğeri slow mu?",
    "Öpücük Kalitesi": "Dudaklarında şiir mi var, yoksa aceleyle biten bir paragraf mı?",
    "Ön Sevişme": "Tansiyonu yavaşça mı yükseltir, yoksa doğrudan hızlı moda mı geçer?",
    "Yatakta Yaratıcılık": "Sürprizlerle şaşırtır mı, yoksa tek sahnelik bir senaryo mu var?",
    "Fanteziye Açıklık": "Yeni fikirlere açık mı, yoksa ‘ben klasik severim’ mi der?",
    "Cinsel İstek": "Tutkulu bir enerjiyle mi yaklaşır, yoksa ‘bugün yorgunum’lar hep mi var?"
}

# Türkçe karakter olmayan sütun isimleri ile eşleme
key_map = {
    "Empati": "empati",
    "Güvenilirlik": "guvenilirlik",
    "Duygusallık": "duygusallik",
    "Romantiklik": "romantiklik",
    "Espri Anlayışı": "espri_anlayisi",
    "Zeka": "zeka",
    "Hırs": "hirs",
    "Tutku": "tutku",
    "Sorumluluk": "sorumluluk",
    "Dürüstlük": "durustluk",
    "Kıskançlık": "kiskanclik",
    "Sosyal Hayat": "sosyal_hayat",
    "Seyahat Macera": "seyahat_macera",
    "Fiziksel Çekicilik": "fiziksel_cekicilik",
    "Cinsel Uyum": "cinsel_uyum",
    "Öpücük Kalitesi": "opucuk_kalitesi",
    "Ön Sevişme": "on_sevisme",
    "Yatakta Yaratıcılık": "yatakta_yaraticilik",
    "Fanteziye Açıklık": "fanteziye_aciklik",
    "Cinsel İstek": "cinsel_istek"
}

# Form puanlarını temizleyip int yapar
def clean_score(val):
    try:
        return int(val)
    except (TypeError, ValueError):
        return 0

@app.route("/", methods=["GET", "POST"])
def form():
    if request.method == "POST":
        kodad = request.form.get("kodad")
        isim = request.form.get("isim")
        puanlar = {soru: clean_score(request.form.get(soru)) for soru in sorular}

        conn = get_db_connection()
        cursor = conn.cursor()

        sql = f"""
        INSERT INTO ratings (
            kod_adi, ex_ismi, {', '.join(key_map.values())}
        ) VALUES (%s, %s, {', '.join(['%s'] * len(key_map))})
        """

        values = [kodad, isim] + [puanlar[s] for s in sorular]
        cursor.execute(sql, values)
        conn.commit()
        cursor.close()
        conn.close()

        return redirect(url_for('sonuc', kodad=kodad))

    return render_template("man_rate_form.html", sorular=sorular)

@app.route("/sonuc/<kodad>", methods=["GET"])
def sonuc(kodad):
    conn = get_db_connection()
    cursor = conn.cursor
    cursor.execute("SELECT * FROM ratings WHERE kod_adi = %s ORDER BY id DESC LIMIT 1", (kodad,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()

    if not row:
        return "<h2>Kayıt bulunamadı.</h2>"

    toplam_puan = {soru: row[key_map[soru]] for soru in sorular}

    en_iyi = [(s, p) for s, p in toplam_puan.items() if p >= 8]
    en_kotu = [(s, p) for s, p in toplam_puan.items() if p <= 3]

    if not en_iyi:
        en_iyi = sorted(toplam_puan.items(), key=lambda x: x[1], reverse=True)[:3]
    if not en_kotu:
        en_kotu = sorted(toplam_puan.items(), key=lambda x: x[1])[:3]

    iyi_ozellik = random.choice(en_iyi)[0] if en_iyi else "Belirlenemedi"
    kotu_ozellik = random.choice(en_kotu)[0] if en_kotu else "Belirlenemedi"

    sonuc_yazisi = f"{kodad}’nın tipi belli oldu: {iyi_ozellik} var, fakat {kotu_ozellik} yok!"
    overall_score = round(sum(toplam_puan.values()) / len(toplam_puan), 2)

    return render_template(
        "man_rate_result.html",
        kodad=kodad,
        sonuc_yazisi=sonuc_yazisi,
        overall_score=overall_score,
        form_link=request.host_url.rstrip('/') + url_for('form'),
        iyi_ozellik=iyi_ozellik,
        kotu_ozellik=kotu_ozellik
    )

@app.route("/veriler")
def veriler():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ratings ORDER BY id DESC")
    veri_listesi = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    cursor.close()
    conn.close()
    return render_template("man_rate_veriler.html", veri_listesi=veri_listesi, columns=columns)

@app.route("/tablo")
def tablo():
    conn = get_db_connection()
    cursor = conn.cursor
    cursor.execute("SELECT * FROM ratings")
    veriler = cursor.fetchall()
    cursor.close()
    conn.close()

    if not veriler:
        return render_template(
            "man_rate_table.html",
            en_iyiler={},
            en_kotuler={},
            ortalamalar={},
            sorular=[],
            toplam_giris_sayisi=0
        )

    toplam_giris_sayisi = len(veriler)
    ortalamalar = {}
    en_iyiler = {}
    en_kotuler = {}

    for soru, key in key_map.items():
        degerler = [(v["kod_adi"], v.get(key, 0)) for v in veriler if isinstance(v.get(key), (int, float))]
        if degerler:
            ort = round(sum(p for _, p in degerler) / len(degerler), 2)
            ortalamalar[soru] = ort
            en_iyiler[soru] = sorted(degerler, key=lambda x: x[1], reverse=True)[:5]
            en_kotuler[soru] = sorted(degerler, key=lambda x: x[1])[:5]
        else:
            ortalamalar[soru] = "N/A"
            en_iyiler[soru] = []
            en_kotuler[soru] = []

    return render_template(
        "man_rate_table.html",
        en_iyiler=en_iyiler,
        en_kotuler=en_kotuler,
        sorular=list(sorular.keys()),
        ortalamalar=ortalamalar,
        toplam_giris_sayisi=toplam_giris_sayisi
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
