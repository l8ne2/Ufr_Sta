"""
UFR STA - Site Web Vitrine
Université Amadou Mahtar Mbow (UAM) de Dakar
Projet final - Programmation Web (Dr Lamine YADE)

Application Flask + SQLite
"""

import os
import sqlite3
import uuid
from datetime import datetime
from functools import wraps

from flask import (
    Flask, render_template, request, redirect, url_for,
    session, flash, g, abort
)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database", "ufr_sta.db")
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

app = Flask(__name__)
app.config["SECRET_KEY"] = "ufr-sta-secret-key-changer-en-production"
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10 Mo par requête


# ---------------------------------------------------------------------------
# Gestion des fichiers uploadés (photos)
# ---------------------------------------------------------------------------

def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


def save_uploaded_file(file_storage, subfolder):
    """Enregistre un fichier uploadé dans static/uploads/<subfolder>/
    et renvoie le chemin web (ex: /static/uploads/actualites/xxx.jpg),
    ou None si aucun fichier valide n'a été fourni."""
    if not file_storage or file_storage.filename == "":
        return None
    if not allowed_file(file_storage.filename):
        flash(
            "Format de fichier non autorisé. Formats acceptés : "
            "jpg, jpeg, png, gif, webp.", "danger"
        )
        return None
    ext = file_storage.filename.rsplit(".", 1)[1].lower()
    filename = secure_filename(f"{uuid.uuid4().hex}.{ext}")
    folder = os.path.join(UPLOAD_FOLDER, subfolder)
    os.makedirs(folder, exist_ok=True)
    file_storage.save(os.path.join(folder, filename))
    return f"/static/uploads/{subfolder}/{filename}"


def delete_uploaded_file(web_path):
    """Supprime physiquement un fichier précédemment uploadé, si présent."""
    if not web_path or not web_path.startswith("/static/uploads/"):
        return
    real_path = os.path.join(BASE_DIR, web_path.lstrip("/"))
    if os.path.exists(real_path):
        try:
            os.remove(real_path)
        except OSError:
            pass


# ---------------------------------------------------------------------------
# Connexion base de données
# ---------------------------------------------------------------------------

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    os.makedirs(os.path.join(BASE_DIR, "database"), exist_ok=True)
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    with open(os.path.join(BASE_DIR, "database", "schema.sql"), "r", encoding="utf-8") as f:
        db.executescript(f.read())

    # Créer un compte admin par défaut si aucun n'existe
    cur = db.execute("SELECT COUNT(*) AS c FROM admins")
    if cur.fetchone()["c"] == 0:
        db.execute(
            "INSERT INTO admins (username, password_hash) VALUES (?, ?)",
            ("admin", generate_password_hash("admin123")),
        )

    # Données de démonstration si la base est vide
    cur = db.execute("SELECT COUNT(*) AS c FROM departements")
    if cur.fetchone()["c"] == 0:
        seed_demo_data(db)

    db.commit()
    db.close()


def seed_demo_data(db):
    departements = [
        ("MIM", "Département Mathématiques, Informatique et Modélisation — regroupe les "
                "mentions Mathématiques et Modélisation (MM) et Informatique.",
         "Dr Thierno Mohamadane Mansour Sow", "thierno.sow@uam.edu.sn"),
        ("SMU", "Département Sciences de la Mer et de l'Univers — regroupe les mentions "
                "Physique et Applications (PA) et Sciences de la Mer et du Littoral (SML).",
         "Dr Makha Ndao", "makha.ndao@uam.edu.sn"),
    ]
    for d in departements:
        db.execute(
            "INSERT INTO departements (nom, description, responsable, contact) VALUES (?,?,?,?)", d
        )

    dep_ids = {r["nom"]: r["id"] for r in db.execute("SELECT id, nom FROM departements")}

    # --- Formations (filières) ---
    formations = [
        ("Licence MPI — Mathématiques, Physique et Informatique", "Licence", "3 ans",
         "Bac scientifique ou technique", "Développeur, Data analyst, Enseignant, Chercheur",
         dep_ids["MIM"],
         "S1: Algorithmique, Mathématiques, Logique, Physique générale\n"
         "S2: Programmation, Algèbre, Analyse, Systèmes"),
        ("Licence SML — Sciences de la Mer et du Littoral", "Licence", "3 ans",
         "Bac scientifique", "Ingénieur halieutique, Chercheur, Gestionnaire du littoral",
         dep_ids["SMU"],
         "S1: Océanographie générale, Physique, Chimie marine, Mathématiques\n"
         "S2: Biologie marine, Écologie littorale, Cartographie"),
    ]
    for f in formations:
        db.execute(
            """INSERT INTO formations
               (nom, niveau, duree, conditions_admission, debouches, departement_id, programme)
               VALUES (?,?,?,?,?,?,?)""", f
        )

    # --- Actualités ---
    actualites = [
        ("Continuité pédagogique en ligne : réunion d'information et de concertation",
         "2026-06-27",
         "Dans le cadre des Jeux Olympiques de la Jeunesse Dakar 2026, l'UFR STA a réuni "
         "enseignants-chercheurs et personnel administratif autour du dispositif de continuité "
         "pédagogique en ligne (plateforme Moodle, activités synchrones/asynchrones, évaluations).",
         "/static/images/reunion_continuite_pedagogique.jpg"),
        ("Appel à candidature : Enseignant-chercheur en Mathématiques Appliquées",
         "2026-06-15",
         "L'UAM recrute un(e) enseignant(e)-chercheur(se) en Mathématiques Appliquées "
         "(Statistique, Big Data et/ou Économétrie). Candidatures en ligne sur depot.uam.sn/per "
         "avant le 15 juin 2026 à 23h59.",
         "/static/images/actu_recrutement_maths.jpg"),
    ]
    for a in actualites:
        db.execute(
            "INSERT INTO actualites (titre, date_pub, description, photo) VALUES (?,?,?,?)", a
        )

    # --- Activités ---
    activites = [
        ("Participation à la Journée internationale des gens de mer (ANAM)",
         "2026-06-25",
         "Grand Théâtre National Doudou Ndiaye Rose, Dakar",
         "Agence Nationale des Affaires Maritimes (ANAM)",
         "Les étudiants de l'UFR STA, accompagnés du Dr Makha Ndao et du Pr Issa Sakho, ont "
         "participé à la 7ᵉ édition de cette journée et tenu un stand de présentation des "
         "formations de l'UFR, remarqué notamment par le Directeur général de l'ANAM.",
         "/static/images/anam_journee_gens_mer.jpg"),
        ("Journée de l'Excellence de l'UFR STA",
         "2026-05-09",
         "Université Amadou Mahtar Mbow (UAM)",
         "Amicale des Étudiants de l'UFR STA (M. Moctar Sall)",
         "Sous le parrainage du Pr Amadou Dahirou Gueye, cette journée a célébré le mérite "
         "académique : distinction des cinq meilleurs étudiants de l'UFR, de l'équipe championne, "
         "suivie d'un concours de génie en herbe.",
         "/static/images/journee_excellence_1.jpg\n/static/images/journee_excellence_2.jpg"),
    ]
    for act in activites:
        db.execute(
            """INSERT INTO activites (titre, date_act, lieu, organisateur, description, photos)
               VALUES (?,?,?,?,?,?)""", act
        )

    # --- Galerie photos ---
    albums = [
        ("Journée de l'Excellence 2026",
         "Cérémonie de distinction des meilleurs étudiants et concours de génie en herbe.",
         "2026-05-09"),
    ]
    album_photo_files = {
        "Journée de l'Excellence 2026": [
            "/static/images/excellence_anam_groupe.jpg",
            "/static/images/excellence_audience.jpg",
            "/static/images/excellence_remise_medailles.jpg",
            "/static/images/excellence_ruban.jpg",
        ],
    }
    for al in albums:
        cur = db.execute(
            "INSERT INTO albums (titre, description, date_album) VALUES (?,?,?)", al
        )
        album_id = cur.lastrowid
        for url in album_photo_files.get(al[0], []):
            db.execute(
                "INSERT INTO album_photos (album_id, url) VALUES (?, ?)", (album_id, url)
            )

    # --- Enseignants ---
    enseignants = [
        ("Amadou Dahirou Gueye", "Enseignant-chercheur", dep_ids["MIM"],
         "dahirou.gueye@uam.edu.sn",
         "Recruté à l'UAM le 02/11/2023 ; ex-enseignant-chercheur à l'Université "
         "Alioune Diop de Bambey (2008–2023).",
         "/static/images/ens_amadou_dahirou_gueye.jpg"),
        ("Thierno Mohamadane Mansour Sow",
         "Chef du Département Mathématiques, Informatique et Modélisation (MIM)",
         dep_ids["MIM"], "thierno.sow@uam.edu.sn", "",
         "/static/images/ens_thierno_sow.jpg"),
        ("Makha Ndao",
         "Chef du Département Sciences de la Mer et de l'Univers (SMU)",
         dep_ids["SMU"], "makha.ndao@uam.edu.sn", "",
         "/static/images/ens_makha_ndao.jpg"),
    ]
    for e in enseignants:
        db.execute(
            """INSERT INTO enseignants (nom, grade, departement_id, email, domaines_recherche, photo)
               VALUES (?,?,?,?,?,?)""", e
        )


# ---------------------------------------------------------------------------
# Sécurité admin
# ---------------------------------------------------------------------------

def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("admin_id"):
            flash("Veuillez vous connecter pour accéder à l'administration.", "warning")
            return redirect(url_for("login", next=request.path))
        return view(*args, **kwargs)
    return wrapped


@app.context_processor
def inject_globals():
    return {"current_year": datetime.now().year}


# ---------------------------------------------------------------------------
# Pages publiques
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    db = get_db()
    actualites = db.execute(
        "SELECT * FROM actualites ORDER BY date_pub DESC LIMIT 3"
    ).fetchall()
    departements = db.execute("SELECT * FROM departements ORDER BY nom").fetchall()
    return render_template("index.html", actualites=actualites, departements=departements)


@app.route("/departements")
def departements():
    db = get_db()
    deps = db.execute("SELECT * FROM departements ORDER BY nom").fetchall()
    return render_template("departements.html", departements=deps)


@app.route("/departements/<int:dep_id>")
def departement_detail(dep_id):
    db = get_db()
    dep = db.execute("SELECT * FROM departements WHERE id=?", (dep_id,)).fetchone()
    if dep is None:
        abort(404)
    formations = db.execute(
        "SELECT * FROM formations WHERE departement_id=? ORDER BY nom", (dep_id,)
    ).fetchall()
    enseignants = db.execute(
        "SELECT * FROM enseignants WHERE departement_id=? ORDER BY nom", (dep_id,)
    ).fetchall()
    return render_template(
        "departement_detail.html", dep=dep, formations=formations, enseignants=enseignants
    )


@app.route("/formations")
def formations():
    db = get_db()
    forms = db.execute(
        """SELECT f.*, d.nom AS departement_nom FROM formations f
           LEFT JOIN departements d ON d.id = f.departement_id
           ORDER BY f.nom"""
    ).fetchall()
    return render_template("formations.html", formations=forms)


@app.route("/formations/<int:form_id>")
def formation_detail(form_id):
    db = get_db()
    formation = db.execute(
        """SELECT f.*, d.nom AS departement_nom FROM formations f
           LEFT JOIN departements d ON d.id = f.departement_id
           WHERE f.id=?""", (form_id,)
    ).fetchone()
    if formation is None:
        abort(404)
    return render_template("formation_detail.html", formation=formation)


@app.route("/actualites")
def actualites():
    db = get_db()
    news = db.execute("SELECT * FROM actualites ORDER BY date_pub DESC").fetchall()
    return render_template("actualites.html", actualites=news)


@app.route("/actualites/<int:news_id>")
def actualite_detail(news_id):
    db = get_db()
    news = db.execute("SELECT * FROM actualites WHERE id=?", (news_id,)).fetchone()
    if news is None:
        abort(404)
    return render_template("actualite_detail.html", news=news)


@app.route("/activites")
def activites():
    db = get_db()
    acts = db.execute("SELECT * FROM activites ORDER BY date_act DESC").fetchall()
    return render_template("activites.html", activites=acts)


@app.route("/activites/<int:act_id>")
def activite_detail(act_id):
    db = get_db()
    act = db.execute("SELECT * FROM activites WHERE id=?", (act_id,)).fetchone()
    if act is None:
        abort(404)
    photos = [p.strip() for p in (act["photos"] or "").splitlines() if p.strip()]
    return render_template("activite_detail.html", act=act, photos=photos)


@app.route("/enseignants")
def enseignants():
    db = get_db()
    ens = db.execute(
        """SELECT e.*, d.nom AS departement_nom FROM enseignants e
           LEFT JOIN departements d ON d.id = e.departement_id
           ORDER BY e.nom"""
    ).fetchall()
    return render_template("enseignants.html", enseignants=ens)


@app.route("/galerie")
def galerie():
    db = get_db()
    albums = db.execute("SELECT * FROM albums ORDER BY date_album DESC").fetchall()
    albums_data = []
    for al in albums:
        photos = db.execute(
            "SELECT * FROM album_photos WHERE album_id=? ORDER BY id", (al["id"],)
        ).fetchall()
        albums_data.append({"album": al, "photos": photos})
    return render_template("galerie.html", albums_data=albums_data)


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        nom = request.form.get("nom", "").strip()
        email = request.form.get("email", "").strip()
        sujet = request.form.get("sujet", "").strip()
        message = request.form.get("message", "").strip()

        if not nom or not email or not message:
            flash("Merci de remplir tous les champs obligatoires.", "danger")
        else:
            db = get_db()
            db.execute(
                """INSERT INTO messages (nom, email, sujet, message, date_envoi)
                   VALUES (?,?,?,?,?)""",
                (nom, email, sujet, message, datetime.now().strftime("%Y-%m-%d %H:%M")),
            )
            db.commit()
            flash("Votre message a bien été envoyé. Merci de nous avoir contactés !", "success")
            return redirect(url_for("contact"))

    return render_template("contact.html")


# ---------------------------------------------------------------------------
# Authentification admin
# ---------------------------------------------------------------------------

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        db = get_db()
        admin = db.execute(
            "SELECT * FROM admins WHERE username=?", (username,)
        ).fetchone()
        if admin and check_password_hash(admin["password_hash"], password):
            session.clear()
            session["admin_id"] = admin["id"]
            session["admin_username"] = admin["username"]
            flash(f"Bienvenue, {admin['username']} !", "success")
            next_url = request.args.get("next") or url_for("admin_dashboard")
            return redirect(next_url)
        flash("Identifiants incorrects.", "danger")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Vous avez été déconnecté.", "success")
    return redirect(url_for("login"))


# ---------------------------------------------------------------------------
# Administration - Dashboard
# ---------------------------------------------------------------------------

@app.route("/admin")
@login_required
def admin_dashboard():
    db = get_db()
    stats = {
        "actualites": db.execute("SELECT COUNT(*) c FROM actualites").fetchone()["c"],
        "activites": db.execute("SELECT COUNT(*) c FROM activites").fetchone()["c"],
        "formations": db.execute("SELECT COUNT(*) c FROM formations").fetchone()["c"],
        "departements": db.execute("SELECT COUNT(*) c FROM departements").fetchone()["c"],
        "enseignants": db.execute("SELECT COUNT(*) c FROM enseignants").fetchone()["c"],
        "albums": db.execute("SELECT COUNT(*) c FROM albums").fetchone()["c"],
        "messages": db.execute("SELECT COUNT(*) c FROM messages").fetchone()["c"],
    }
    dernieres_actus = db.execute(
        "SELECT * FROM actualites ORDER BY date_pub DESC LIMIT 5"
    ).fetchall()
    derniers_messages = db.execute(
        "SELECT * FROM messages ORDER BY id DESC LIMIT 5"
    ).fetchall()
    return render_template(
        "admin/dashboard.html", stats=stats,
        dernieres_actus=dernieres_actus, derniers_messages=derniers_messages
    )


# ---------------------------------------------------------------------------
# Administration - Actualités (CRUD)
# ---------------------------------------------------------------------------

@app.route("/admin/actualites")
@login_required
def admin_actualites():
    db = get_db()
    news = db.execute("SELECT * FROM actualites ORDER BY date_pub DESC").fetchall()
    return render_template("admin/actualites.html", actualites=news)


@app.route("/admin/actualites/ajouter", methods=["GET", "POST"])
@login_required
def admin_actualite_add():
    if request.method == "POST":
        db = get_db()
        photo_path = save_uploaded_file(request.files.get("photo"), "actualites") or ""
        db.execute(
            "INSERT INTO actualites (titre, date_pub, description, photo) VALUES (?,?,?,?)",
            (request.form["titre"], request.form["date_pub"],
             request.form["description"], photo_path),
        )
        db.commit()
        flash("Actualité ajoutée avec succès.", "success")
        return redirect(url_for("admin_actualites"))
    return render_template("admin/actualite_form.html", item=None)


@app.route("/admin/actualites/<int:item_id>/modifier", methods=["GET", "POST"])
@login_required
def admin_actualite_edit(item_id):
    db = get_db()
    item = db.execute("SELECT * FROM actualites WHERE id=?", (item_id,)).fetchone()
    if item is None:
        abort(404)
    if request.method == "POST":
        photo_path = item["photo"]
        new_photo = save_uploaded_file(request.files.get("photo"), "actualites")
        if new_photo:
            delete_uploaded_file(item["photo"])
            photo_path = new_photo
        elif request.form.get("remove_photo"):
            delete_uploaded_file(item["photo"])
            photo_path = ""
        db.execute(
            "UPDATE actualites SET titre=?, date_pub=?, description=?, photo=? WHERE id=?",
            (request.form["titre"], request.form["date_pub"],
             request.form["description"], photo_path, item_id),
        )
        db.commit()
        flash("Actualité modifiée avec succès.", "success")
        return redirect(url_for("admin_actualites"))
    return render_template("admin/actualite_form.html", item=item)


@app.route("/admin/actualites/<int:item_id>/supprimer", methods=["POST"])
@login_required
def admin_actualite_delete(item_id):
    db = get_db()
    item = db.execute("SELECT * FROM actualites WHERE id=?", (item_id,)).fetchone()
    if item:
        delete_uploaded_file(item["photo"])
    db.execute("DELETE FROM actualites WHERE id=?", (item_id,))
    db.commit()
    flash("Actualité supprimée.", "success")
    return redirect(url_for("admin_actualites"))


# ---------------------------------------------------------------------------
# Administration - Activités (CRUD)
# ---------------------------------------------------------------------------

@app.route("/admin/activites")
@login_required
def admin_activites():
    db = get_db()
    acts = db.execute("SELECT * FROM activites ORDER BY date_act DESC").fetchall()
    return render_template("admin/activites.html", activites=acts)


@app.route("/admin/activites/ajouter", methods=["GET", "POST"])
@login_required
def admin_activite_add():
    if request.method == "POST":
        db = get_db()
        saved_paths = []
        for f in request.files.getlist("photos"):
            p = save_uploaded_file(f, "activites")
            if p:
                saved_paths.append(p)
        db.execute(
            """INSERT INTO activites (titre, date_act, lieu, organisateur, description, photos)
               VALUES (?,?,?,?,?,?)""",
            (request.form["titre"], request.form["date_act"], request.form["lieu"],
             request.form["organisateur"], request.form["description"],
             "\n".join(saved_paths)),
        )
        db.commit()
        flash("Activité ajoutée avec succès.", "success")
        return redirect(url_for("admin_activites"))
    return render_template("admin/activite_form.html", item=None, existing_photos=[])


@app.route("/admin/activites/<int:item_id>/modifier", methods=["GET", "POST"])
@login_required
def admin_activite_edit(item_id):
    db = get_db()
    item = db.execute("SELECT * FROM activites WHERE id=?", (item_id,)).fetchone()
    if item is None:
        abort(404)
    existing_photos = [p for p in (item["photos"] or "").splitlines() if p.strip()]
    if request.method == "POST":
        to_remove = request.form.getlist("remove_photos")
        for p in to_remove:
            delete_uploaded_file(p)
        remaining = [p for p in existing_photos if p not in to_remove]
        for f in request.files.getlist("photos"):
            saved = save_uploaded_file(f, "activites")
            if saved:
                remaining.append(saved)
        db.execute(
            """UPDATE activites SET titre=?, date_act=?, lieu=?, organisateur=?,
               description=?, photos=? WHERE id=?""",
            (request.form["titre"], request.form["date_act"], request.form["lieu"],
             request.form["organisateur"], request.form["description"],
             "\n".join(remaining), item_id),
        )
        db.commit()
        flash("Activité modifiée avec succès.", "success")
        return redirect(url_for("admin_activites"))
    return render_template("admin/activite_form.html", item=item, existing_photos=existing_photos)


@app.route("/admin/activites/<int:item_id>/supprimer", methods=["POST"])
@login_required
def admin_activite_delete(item_id):
    db = get_db()
    item = db.execute("SELECT * FROM activites WHERE id=?", (item_id,)).fetchone()
    if item:
        for p in (item["photos"] or "").splitlines():
            delete_uploaded_file(p.strip())
    db.execute("DELETE FROM activites WHERE id=?", (item_id,))
    db.commit()
    flash("Activité supprimée.", "success")
    return redirect(url_for("admin_activites"))


# ---------------------------------------------------------------------------
# Administration - Formations (CRUD)
# ---------------------------------------------------------------------------

@app.route("/admin/formations")
@login_required
def admin_formations():
    db = get_db()
    forms = db.execute(
        """SELECT f.*, d.nom AS departement_nom FROM formations f
           LEFT JOIN departements d ON d.id = f.departement_id ORDER BY f.nom"""
    ).fetchall()
    return render_template("admin/formations.html", formations=forms)


@app.route("/admin/formations/ajouter", methods=["GET", "POST"])
@login_required
def admin_formation_add():
    db = get_db()
    if request.method == "POST":
        db.execute(
            """INSERT INTO formations
               (nom, niveau, duree, conditions_admission, debouches, departement_id, programme)
               VALUES (?,?,?,?,?,?,?)""",
            (request.form["nom"], request.form["niveau"], request.form["duree"],
             request.form["conditions_admission"], request.form["debouches"],
             request.form["departement_id"], request.form["programme"]),
        )
        db.commit()
        flash("Formation ajoutée avec succès.", "success")
        return redirect(url_for("admin_formations"))
    deps = db.execute("SELECT * FROM departements ORDER BY nom").fetchall()
    return render_template("admin/formation_form.html", item=None, departements=deps)


@app.route("/admin/formations/<int:item_id>/modifier", methods=["GET", "POST"])
@login_required
def admin_formation_edit(item_id):
    db = get_db()
    item = db.execute("SELECT * FROM formations WHERE id=?", (item_id,)).fetchone()
    if item is None:
        abort(404)
    if request.method == "POST":
        db.execute(
            """UPDATE formations SET nom=?, niveau=?, duree=?, conditions_admission=?,
               debouches=?, departement_id=?, programme=? WHERE id=?""",
            (request.form["nom"], request.form["niveau"], request.form["duree"],
             request.form["conditions_admission"], request.form["debouches"],
             request.form["departement_id"], request.form["programme"], item_id),
        )
        db.commit()
        flash("Formation modifiée avec succès.", "success")
        return redirect(url_for("admin_formations"))
    deps = db.execute("SELECT * FROM departements ORDER BY nom").fetchall()
    return render_template("admin/formation_form.html", item=item, departements=deps)


@app.route("/admin/formations/<int:item_id>/supprimer", methods=["POST"])
@login_required
def admin_formation_delete(item_id):
    db = get_db()
    db.execute("DELETE FROM formations WHERE id=?", (item_id,))
    db.commit()
    flash("Formation supprimée.", "success")
    return redirect(url_for("admin_formations"))


# ---------------------------------------------------------------------------
# Administration - Départements (CRUD)
# ---------------------------------------------------------------------------

@app.route("/admin/departements")
@login_required
def admin_departements():
    db = get_db()
    deps = db.execute("SELECT * FROM departements ORDER BY nom").fetchall()
    return render_template("admin/departements.html", departements=deps)


@app.route("/admin/departements/ajouter", methods=["GET", "POST"])
@login_required
def admin_departement_add():
    if request.method == "POST":
        db = get_db()
        db.execute(
            "INSERT INTO departements (nom, description, responsable, contact) VALUES (?,?,?,?)",
            (request.form["nom"], request.form["description"],
             request.form["responsable"], request.form["contact"]),
        )
        db.commit()
        flash("Département ajouté avec succès.", "success")
        return redirect(url_for("admin_departements"))
    return render_template("admin/departement_form.html", item=None)


@app.route("/admin/departements/<int:item_id>/modifier", methods=["GET", "POST"])
@login_required
def admin_departement_edit(item_id):
    db = get_db()
    item = db.execute("SELECT * FROM departements WHERE id=?", (item_id,)).fetchone()
    if item is None:
        abort(404)
    if request.method == "POST":
        db.execute(
            "UPDATE departements SET nom=?, description=?, responsable=?, contact=? WHERE id=?",
            (request.form["nom"], request.form["description"],
             request.form["responsable"], request.form["contact"], item_id),
        )
        db.commit()
        flash("Département modifié avec succès.", "success")
        return redirect(url_for("admin_departements"))
    return render_template("admin/departement_form.html", item=item)


@app.route("/admin/departements/<int:item_id>/supprimer", methods=["POST"])
@login_required
def admin_departement_delete(item_id):
    db = get_db()
    db.execute("DELETE FROM departements WHERE id=?", (item_id,))
    db.commit()
    flash("Département supprimé.", "success")
    return redirect(url_for("admin_departements"))


# ---------------------------------------------------------------------------
# Administration - Enseignants (CRUD)
# ---------------------------------------------------------------------------

@app.route("/admin/enseignants")
@login_required
def admin_enseignants():
    db = get_db()
    ens = db.execute(
        """SELECT e.*, d.nom AS departement_nom FROM enseignants e
           LEFT JOIN departements d ON d.id = e.departement_id ORDER BY e.nom"""
    ).fetchall()
    return render_template("admin/enseignants.html", enseignants=ens)


@app.route("/admin/enseignants/ajouter", methods=["GET", "POST"])
@login_required
def admin_enseignant_add():
    db = get_db()
    if request.method == "POST":
        photo_path = save_uploaded_file(request.files.get("photo"), "enseignants") or ""
        db.execute(
            """INSERT INTO enseignants (nom, grade, departement_id, email, domaines_recherche, photo)
               VALUES (?,?,?,?,?,?)""",
            (request.form["nom"], request.form["grade"], request.form["departement_id"],
             request.form["email"], request.form["domaines_recherche"], photo_path),
        )
        db.commit()
        flash("Enseignant ajouté avec succès.", "success")
        return redirect(url_for("admin_enseignants"))
    deps = db.execute("SELECT * FROM departements ORDER BY nom").fetchall()
    return render_template("admin/enseignant_form.html", item=None, departements=deps)


@app.route("/admin/enseignants/<int:item_id>/modifier", methods=["GET", "POST"])
@login_required
def admin_enseignant_edit(item_id):
    db = get_db()
    item = db.execute("SELECT * FROM enseignants WHERE id=?", (item_id,)).fetchone()
    if item is None:
        abort(404)
    if request.method == "POST":
        photo_path = item["photo"]
        new_photo = save_uploaded_file(request.files.get("photo"), "enseignants")
        if new_photo:
            delete_uploaded_file(item["photo"])
            photo_path = new_photo
        elif request.form.get("remove_photo"):
            delete_uploaded_file(item["photo"])
            photo_path = ""
        db.execute(
            """UPDATE enseignants SET nom=?, grade=?, departement_id=?, email=?,
               domaines_recherche=?, photo=? WHERE id=?""",
            (request.form["nom"], request.form["grade"], request.form["departement_id"],
             request.form["email"], request.form["domaines_recherche"],
             photo_path, item_id),
        )
        db.commit()
        flash("Enseignant modifié avec succès.", "success")
        return redirect(url_for("admin_enseignants"))
    deps = db.execute("SELECT * FROM departements ORDER BY nom").fetchall()
    return render_template("admin/enseignant_form.html", item=item, departements=deps)


@app.route("/admin/enseignants/<int:item_id>/supprimer", methods=["POST"])
@login_required
def admin_enseignant_delete(item_id):
    db = get_db()
    item = db.execute("SELECT * FROM enseignants WHERE id=?", (item_id,)).fetchone()
    if item:
        delete_uploaded_file(item["photo"])
    db.execute("DELETE FROM enseignants WHERE id=?", (item_id,))
    db.commit()
    flash("Enseignant supprimé.", "success")
    return redirect(url_for("admin_enseignants"))


# ---------------------------------------------------------------------------
# Administration - Galerie (albums + photos) (CRUD)
# ---------------------------------------------------------------------------

@app.route("/admin/galerie")
@login_required
def admin_galerie():
    db = get_db()
    albums = db.execute("SELECT * FROM albums ORDER BY date_album DESC").fetchall()
    albums_data = []
    for al in albums:
        photos = db.execute(
            "SELECT * FROM album_photos WHERE album_id=? ORDER BY id", (al["id"],)
        ).fetchall()
        albums_data.append({"album": al, "photos": photos})
    return render_template("admin/galerie.html", albums_data=albums_data)


@app.route("/admin/galerie/ajouter", methods=["GET", "POST"])
@login_required
def admin_album_add():
    if request.method == "POST":
        db = get_db()
        cur = db.execute(
            "INSERT INTO albums (titre, description, date_album) VALUES (?,?,?)",
            (request.form["titre"], request.form["description"], request.form["date_album"]),
        )
        album_id = cur.lastrowid
        for f in request.files.getlist("photos"):
            p = save_uploaded_file(f, "albums")
            if p:
                db.execute(
                    "INSERT INTO album_photos (album_id, url) VALUES (?, ?)", (album_id, p)
                )
        db.commit()
        flash("Album ajouté avec succès.", "success")
        return redirect(url_for("admin_galerie"))
    return render_template("admin/album_form.html", item=None, existing_photos=[])


@app.route("/admin/galerie/<int:album_id>/modifier", methods=["GET", "POST"])
@login_required
def admin_album_edit(album_id):
    db = get_db()
    item = db.execute("SELECT * FROM albums WHERE id=?", (album_id,)).fetchone()
    if item is None:
        abort(404)
    existing_photos = db.execute(
        "SELECT * FROM album_photos WHERE album_id=? ORDER BY id", (album_id,)
    ).fetchall()
    if request.method == "POST":
        db.execute(
            "UPDATE albums SET titre=?, description=?, date_album=? WHERE id=?",
            (request.form["titre"], request.form["description"],
             request.form["date_album"], album_id),
        )
        remove_ids = {int(i) for i in request.form.getlist("remove_photos")}
        for photo in existing_photos:
            if photo["id"] in remove_ids:
                delete_uploaded_file(photo["url"])
                db.execute("DELETE FROM album_photos WHERE id=?", (photo["id"],))
        for f in request.files.getlist("photos"):
            p = save_uploaded_file(f, "albums")
            if p:
                db.execute(
                    "INSERT INTO album_photos (album_id, url) VALUES (?, ?)", (album_id, p)
                )
        db.commit()
        flash("Album modifié avec succès.", "success")
        return redirect(url_for("admin_galerie"))
    return render_template("admin/album_form.html", item=item, existing_photos=existing_photos)


@app.route("/admin/galerie/<int:album_id>/supprimer", methods=["POST"])
@login_required
def admin_album_delete(album_id):
    db = get_db()
    photos = db.execute("SELECT * FROM album_photos WHERE album_id=?", (album_id,)).fetchall()
    for p in photos:
        delete_uploaded_file(p["url"])
    db.execute("DELETE FROM album_photos WHERE album_id=?", (album_id,))
    db.execute("DELETE FROM albums WHERE id=?", (album_id,))
    db.commit()
    flash("Album supprimé.", "success")
    return redirect(url_for("admin_galerie"))


# ---------------------------------------------------------------------------
# Administration - Messages de contact
# ---------------------------------------------------------------------------

@app.route("/admin/messages")
@login_required
def admin_messages():
    db = get_db()
    msgs = db.execute("SELECT * FROM messages ORDER BY id DESC").fetchall()
    return render_template("admin/messages.html", messages=msgs)


@app.route("/admin/messages/<int:msg_id>/supprimer", methods=["POST"])
@login_required
def admin_message_delete(msg_id):
    db = get_db()
    db.execute("DELETE FROM messages WHERE id=?", (msg_id,))
    db.commit()
    flash("Message supprimé.", "success")
    return redirect(url_for("admin_messages"))


# ---------------------------------------------------------------------------
# Gestion des erreurs
# ---------------------------------------------------------------------------

@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    if not os.path.exists(DB_PATH):
        init_db()
    else:
        # S'assure que les tables existent même si le fichier .db est vide
        init_db()
    app.run(debug=True)
