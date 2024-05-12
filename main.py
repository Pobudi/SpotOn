from flask import Flask, render_template
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import FileField, SubmitField
from werkzeug.utils import secure_filename
import os
from django import template
import pandas as pd
import re
from prometheus_flask_exporter import PrometheusMetrics
import logging



register = template.Library()

@register.filter
def get_type(value):
    return type(value).__name__

biggest = int(max([i.split(".")[0] for i in os.listdir("./static/files")]))
class UploadFile(FlaskForm):
    file = FileField("Browse", validators=[FileAllowed(["txt", "csv", "json"])])
    submit = SubmitField("Upload")

app = Flask(__name__)
app.config["SECRET_KEY"] = "secretsecret"
app.config["UPLOAD_FOLDER"] = "static/files"
logging.basicConfig(level=logging.INFO)
logging.info("Setting LOGLEVEL to INFO")

metrics = PrometheusMetrics(app)
metrics.info("app_info", "App Info, this can be anything you want", version="1.7.1")


@app.route('/', methods=['GET', 'POST'])
def upload():
    global biggest
    form = UploadFile()
    details = None
    if form.validate_on_submit():
        biggest += 1
        file = form.file.data
        extension = secure_filename(file.filename).split(".")[-1]
        path = os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'], f"{biggest}.{extension}")
        file.save(path)
        details = make_details(path, extension)
    return render_template("index.html", form=form, error=form.errors, details=details)

def make_details(path, extension):
    info = {"general": {}}
    if extension!="txt":
        df = eval(f"pd.read_{extension}('{path}')")
        info["general"]["Number of rows: "], info["general"]["Number of columns: "] = df.shape[0], df.shape[1]
        if not df.isnull().values.any():
            info["general"]["No nulls in file"] = ""
        else:
            null_columns = [df.columns[i] for i, v in enumerate(sum(df.isnull().values)) if v]
            info["general"]["Nulls present in these columns: "] = ", ".join(null_columns)
        numerical = df.describe()
        info["numerical"] = {}
        for c in numerical:
            col = numerical[c]
            info["numerical"][c] = {"Mean": col["mean"],
                                    "Standard deviation": col["std"],
                                    "Minimal value": col["min"],
                                    "Maximal value": col["max"]
                                    }
    else:
        file = open(path, "r")
        txt = file.read()
        info["general"]["Number of characters: "] = len(txt)
        info["general"]["Number of words: "] = len(txt.split(" "))
        info["general"]["Number of sentences: "] = len(re.split("\. |! |\? ", txt))
        file.close()
    return info


if __name__ == "__main__":
    app.run(port=8080)
