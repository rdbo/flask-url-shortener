import uuid
from flask import Flask, url_for, redirect, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask("test")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
db = SQLAlchemy(app)

class URLBase(db.Model):
    token = db.Column(db.String(32), primary_key=True, unique=True, nullable=False)
    url = db.Column(db.String(2000), unique=True, nullable=False)

    def __init__(self, _url : str):
        self.token = str(uuid.uuid4()).replace("-", "")[:32]
        self.url = _url[:2000]

@app.route("/generated/<token>")
def generated(token):
    return render_template("generated.html", url_token=token)

@app.route("/", methods=["GET", "POST"])
@app.route("/index.html", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url = request.form["url"]
        if str(url) != "" and str(url).find("://") != -1 and str(url.find(".")):
            try:
                duplicated_url = URLBase.query.filter_by(url=url).first()
                if duplicated_url != None:
                    return redirect(url_for("generated", token=duplicated_url.token))
                url_base = URLBase(url)
                db.session.add(url_base)
                db.session.commit()
                return redirect(url_for("generated", token=url_base.token))
            except:
                return redirect(url_for("generated", token="invalid_token"))
        else:
            return redirect(url_for("generated", token="invalid_url"))

    else:
        return render_template("index.html", url_list=URLBase.query.all())

@app.route("/<url_token>")
def url_redirect(url_token):
    url_base = URLBase.query.filter_by(token=url_token).first()
    url = url_base.url
    return redirect(f"{url}")

if __name__ == "__main__":
    db.create_all()
    app.run()