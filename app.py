from datetime import datetime
import os
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# -----------------
# DATA-LAGRING & KONFIGURASJON
# -----------------
gjestebok_meldinger = []

# Her kan du legge til nye navn etterhvert som du lager nye mapper
ALBUM_NAVN = {
    "troms": "Tromsø - 26",
    "reise": "Sommerferie 2026",
    "nytt": "Diverse bilder"
}

# -----------------
# HJELPEFUNKSJONER
# -----------------
def finn_forsidebilde(kategori):
    """Finner første bildefil i en mappe, ignorerer systemfiler."""
    mappe_sti = os.path.join(app.root_path, 'static', 'bilder', 'galleri', kategori)
    if os.path.exists(mappe_sti):
        bilder = [f for f in os.listdir(mappe_sti) 
                  if f.lower().endswith(('.jpg', '.png', '.jpeg')) 
                  and not f.startswith('.')]
        if bilder:
            bilder.sort()
            return bilder[0]
    return None

# Gjør funksjoner tilgjengelig i alle HTML-filer
app.jinja_env.globals.update(finn_forsidebilde=finn_forsidebilde)

# -----------------
# HOVEDSIDER
# -----------------
@app.route("/")
def hjem():
    siste_melding = gjestebok_meldinger[-1] if gjestebok_meldinger else None
    return render_template("index.html", siste_melding=siste_melding)

@app.route("/notiser")
def notiser():
    return render_template("notiser.html")

@app.route("/venner")
def venner():
    return render_template("venner.html")

@app.route("/ikke-trykk")
def ikke_trykk():
    return render_template("ikke_trykk.html")

# -----------------
# GALLERI & BILDER
# -----------------
@app.route('/bilder')
def vis_oversikt():
    base_path = os.path.join(app.root_path, 'static', 'bilder', 'galleri')
    # Hent kun mapper og filtrer bort skjulte systemfiler
    kategorier = [f for f in os.listdir(base_path) 
                  if os.path.isdir(os.path.join(base_path, f)) 
                  and not f.startswith('.')]
    
    # Sender med kategorier og navne-listen
    return render_template('bilder.html', kategorier=kategorier, navne_liste=ALBUM_NAVN)

# Alias for å støtte gammel link-struktur
@app.route('/bilder_gammel')
def bilder():
    return vis_oversikt()

@app.route('/galleri/<kategori>')
def vis_galleri(kategori):
    mappe_sti = os.path.join(app.root_path, 'static', 'bilder', 'galleri', kategori)
    
    if not os.path.exists(mappe_sti):
        return "Denne kategorien finnes ikke."

    # Hent kun bildefiler
    bilder = [f for f in os.listdir(mappe_sti) 
              if f.lower().endswith(('.jpg', '.png', '.jpeg')) 
              and not f.startswith('.')]
    bilder.sort()
    
    return render_template('galleri.html', bildeliste=bilder, kategori=kategori)

# -----------------
# OPPSKRIFTER
# -----------------
@app.route('/oppskrifter')
def oppskrifter():
    valgt_kategori = request.args.get('kategori', 'alle')
    return render_template('oppskrifter/oppskrifter.html', kategori=valgt_kategori)

# -----------------
# GJESTEBOK (Logikk)
# -----------------
@app.route("/gjestebok", methods=["GET", "POST"])
def gjestebok():
    if request.method == "POST":
        navn = request.form.get("bruker_navn")
        melding = request.form.get("bruker_melding")
        tidsstempel = datetime.now().strftime("%d.%m.%Y kl. %H:%M")

        gjestebok_meldinger.append({"navn": navn, "melding": melding, "tid": tidsstempel})
        return redirect(url_for("gjestebok"))

    er_admin = request.args.get("admin") == "ja"
    return render_template("gjestebok.html", meldinger=gjestebok_meldinger, admin_modus=er_admin)

@app.route("/gjestebok/slett/<int:id>", methods=["POST"])
def slett_hilsen(id):
    RIKTIG_KODE = "1234"
    tastet_kode = request.form.get("admin_kode")
    
    if tastet_kode == RIKTIG_KODE:
        if 0 <= id < len(gjestebok_meldinger):
            gjestebok_meldinger.pop(id)
    else:
        print("FEIL KODE FORSØKT!")
    
    return redirect(url_for("gjestebok"))

app.route('/slett_hilsen/<int:id>', methods=['POST'])
def slett_hilsen(id):
    admin_kode = request.form.get('admin_kode')
    
    # 1. Sjekk om koden er riktig (bytt ut 'mittpassord' med din faktiske kode)
    if admin_kode == "mittpassord":
        # 2. Slett fra listen
        # Siden du bruker reverse i HTML, må vi justere indeksen
        # Vi må slette basert på den faktiske indeksen i listen
        if 0 <= id < len(gjestebok_meldinger):
            gjestebok_meldinger.pop(id)
            
            # Valgfritt: Lagre endringen til fil hvis du bruker fil-lagring
            # lagre_meldinger_til_fil(meldinger)
            
            return redirect(url_for('gjestebok_side'))
        
    return "Feil passord eller ugyldig innlegg", 403

# -----------------
# OPPSTART
# -----------------
if __name__ == "__main__":
    app.run(debug=True, port=5001)