import csv

import random

import os

from flask import redirect, url_for, request

from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("man_rate_form.html", sorular=sorular)


sorular = {
    "Empati": "Duyguların radarında mı, yoksa sadece Netflix’in duygusal sahnelerinde mi ağlıyor?",
    "Güvenilirlik": "Sözünde durur mu, yoksa ‘seni ararım’ dediği gibi 3 gün sonra mı hatırlar?",
    "Duygusallık": "Gül yaprağında gözyaşı mı var, yoksa sadece soğuk esprilerle mi yaşıyor?",
    "Romantiklik": "Sürpriz çiçekler mi gönderir, yoksa özel günleri Google Takvim’den mi öğrenir?",
    "Espri Anlayışı": "Kahkahalarla mı güldürür, yoksa espri yaptığı açıklama gerektirir mi?",
    "Zeka": "Sözleriyle etkiler mi, yoksa bulmaca çözerken bile yardım ister mi?",
    "Hırs": "Hedeflerine koşar mı, yoksa motivasyonu ‘yarın başlarım’ mı?",
    "Tutku": "Gözleriyle yakar mı, yoksa ilgisi yalnızca telefon ekranına mı?",
    "Sorumluluk Sahibi Olma": "Planlara sadık mı, yoksa ‘Unuttum yaa’ onun ikinci adı mı?",
    "Dürüstlük": "Gerçekleri mi söyler, yoksa doğruyu biraz süsleyerek mi anlatır?",
    "Kıskançlık Seviyesi": "Tatlı bir sahiplenme mi, yoksa FBI moduna geçen biri mi?",
    "Sosyal Hayat": "Çevresiyle dengede mi, yoksa ya ev kuşu ya da sosyal kelebek mi?",
    "Seyahat ve Macera İsteği": "Uçağa atlayıp kaçmak mı ister, yoksa valizi bile görünce yorulur mu?",
    "Fiziksel Çekicilik": "Bakışlarıyla büyüler mi, yoksa tarzı ‘evden alelacele çıktım’ mı?",
    "Cinsel Uyum": "Birlikte ritmi yakalar mısınız, yoksa biri rock diğeri slow mu?",
    "Öpücük Kalitesi": "Dudaklarında şiir mi var, yoksa aceleyle biten bir paragraf mı?",
    "Ön Sevişme": "Tansiyonu yavaşça mı yükseltir, yoksa doğrudan hızlı moda mı geçer?",
    "Yatakta Yaratıcılık": "Sürprizlerle şaşırtır mı, yoksa tek sahnelik bir senaryo mu var?",
    "Fanteziye Açıklık": "Yeni fikirlere açık mı, yoksa ‘ben klasik severim’ mi der?",
    "Cinsel İstek": "Tutkulu bir enerjiyle mi yaklaşır, yoksa ‘bugün yorgunum’lar hep mi var?"
}

def clean_score(value):
    try:
        value = value.strip()
        if value == "00":
            return 0
        return int(value)
    except:
        return 0  # Hatalıysa 0 olarak ayarla


@app.route("/form", methods=["GET", "POST"])
def form():
    if request.method == "POST":
        kodad = request.form.get("kodad")
        isim = request.form.get("isim")
        puanlar = {soru: clean_score(request.form.get(soru)) for soru in sorular}
        

        with open('veriler.csv', mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if f.tell() == 0:  # Dosya boşsa başlık satırı yaz
                header = ["Kod Adı", "Ex İsmi"] + list(sorular.keys())
                writer.writerow(header)
            row = [kodad, isim] + [puanlar[s] for s in sorular]
            writer.writerow(row)

        return redirect(url_for('sonuc', kodad=kodad))
    return render_template("man_rate_form.html", sorular=sorular)



@app.route("/sonuc/<kodad>", methods=["POST"])
def sonuc(kodad):
    try:
        with open("veriler.csv", newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["Kod Adı"] == kodad:
                    puanlar = {soru: int(row[soru]) for soru in sorular.keys()}
    except FileNotFoundError:
        return f"<h2> </h2>"

    toplam_puan = puanlar

    # 8 ile 10 arasındaki en iyi özellikler
    en_iyi = [(soru, puan) for soru, puan in toplam_puan.items() if 8 <= puan <= 10]
    # 0 ile 3 arasındaki en kötü özellikler
    en_kotu = [(soru, puan) for soru, puan in toplam_puan.items() if 0 <= puan <= 3]

    # Eğer bu aralıkta hiç yoksa tüm puanlardan seçelim (fallback)
    if not en_iyi:
        en_iyi = sorted(toplam_puan.items(), key=lambda x: x[1], reverse=True)[:3]
    if not en_kotu:
        en_kotu = sorted(toplam_puan.items(), key=lambda x: x[1])[:3]

    # Rastgele 1 tane seç
    iyi_ozellik, _ = random.choice(en_iyi)
    kotu_ozellik, _ = random.choice(en_kotu)

    sonuc_yazisi = f"{kodad}’nın tipi belli oldu: {iyi_ozellik} var, fakat {kotu_ozellik} yok!"

    form_link = request.host_url.rstrip('/') + url_for('form')

    overall_score = round(sum(toplam_puan.values()) / len(toplam_puan), 2)

    return render_template("man_rate_result.html",
                           kodad=kodad,
                           sonuc_yazisi=sonuc_yazisi,
                           form_link=form_link,
                           overall_score=overall_score,
                           iyi_ozellik=iyi_ozellik,
                           kotu_ozellik=kotu_ozellik)





@app.route("/veriler")
def veriler_sayfasi():
    try:
        with open("veriler.csv", newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            veri_listesi = list(reader)
    except FileNotFoundError:
        veri_listesi = []

    return render_template("man_rate_veriler.html",
                           veri_listesi=veri_listesi,
                           en_iyiler=[],
                           en_kotuler=[],
                           ozellik_istatistik={},
                           sorular=list(sorular.keys()),
                           message=None)


@app.route("/tablo")
def tablo():
    try:
        with open("veriler.csv", newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            veriler = list(reader)
    except FileNotFoundError:
        veriler = []

    if not veriler:
        return render_template("man_rate_table.html", en_iyiler={}, en_kotuler={}, sorular=[], ortalamalar={}, sayaclar={}, toplam_giris_sayisi=0)

    sorular = [key for key in veriler[0].keys() if key not in ["Kod Adı", "Ex İsmi"]]

    en_iyiler = {}
    en_kotuler = {}
    ortalamalar = {}
    sayaclar = {}

    toplam_giris_sayisi = len(veriler)  # Satır sayısı, her satır 1 oy.

    for soru in sorular:
        degerler = []
        for v in veriler:
            val = v.get(soru)
            try:
                puan = float(val)
                degerler.append((v.get("Kod Adı", "Bilinmeyen"), puan))
            except (ValueError, TypeError):
                continue

        sayaclar[soru] = len(degerler)

        if degerler:
            toplam = sum(puan for _, puan in degerler)
            ortalama = toplam / len(degerler)
            ortalamalar[soru] = round(ortalama, 2)

            sirali = sorted(degerler, key=lambda x: x[1], reverse=True)
            en_iyiler[soru] = sirali[:5]
            en_kotuler[soru] = sirali[-5:]
        else:
            en_iyiler[soru] = []
            en_kotuler[soru] = []
            ortalamalar[soru] = "N/A"

    # Aynı kişi birden fazla özellik için puan vermiş olabilir, toplam giriş sayısı buraya göre
    # çok yüksek çıkabilir. Eğer farklı kod adlarına göre toplam benzersiz giriş sayısı istersen
    # bunu ayrıca hesaplamalıyız. Şimdilik toplam tüm geçerli puan sayısı olarak gösteriyoruz.

    return render_template(
        "man_rate_table.html",
        en_iyiler=en_iyiler,
        en_kotuler=en_kotuler,
        sorular=sorular,
        ortalamalar=ortalamalar,
        sayaclar=sayaclar,
        toplam_giris_sayisi=toplam_giris_sayisi
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
