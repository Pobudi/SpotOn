from flask import Flask, render_template
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import FileField, SubmitField
from werkzeug.utils import secure_filename
import os
import pandas as pd
import re
from prometheus_flask_exporter import PrometheusMetrics
import logging
import numpy as np

# App configuration
app = Flask(__name__)
# !!!!! Change value from "secretsecret" to something more complicated and store it in an
# environment variable !!!!
app.config["SECRET_KEY"] = "secretsecret"
app.config["UPLOAD_FOLDER"] = "static/files"
logging.basicConfig(level=logging.INFO)

# Exposing metrics
metrics = PrometheusMetrics(app)
metrics.info("app_info", description="Application for quick file insight", version="1.7.1")

# Looking for biggest file name value to help with keeping unique names
biggest = int(max(["0"]+[i.split(".")[0] for i in os.listdir("./static/files")]))


# Upload form class
class UploadFile(FlaskForm):
    file = FileField("Browse", validators=[FileAllowed(["txt", "csv", "json"])])
    submit = SubmitField("Upload")


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
        details = make_details(path)
    return render_template("index.html", form=form, error=form.errors, details=details)

def make_details(path):
    """
    :param path: path to file
    :return: dict
    """
    extension = path.split(".")[-1]

    info = {}

    # Information gathering for .json and .csv files
    # 1D data is data that will be displayed in this format:
    # Header
    # Subheader: value
    # 2D data is data that will be displayed in this format:
    # Header
    # Smaller header (column name)
    # Smaller header: value
    if extension!="txt":

        # using pandas to read uploaded file
        df = eval(f"pd.read_{extension}('{path}')")
        numerical = df.describe()

        # General information
        info["1D"] = {}
        info["1D"]["General information"] = {}
        info["1D"]["General information"]["Number of rows: "], info["1D"]["General information"]["Number of columns: "] = df.shape[0], df.shape[1]
        if not df.isnull().values.any():
            info["1D"]["General information"]["No nulls in file"] = ""
        else:
            null_columns = [df.columns[i] for i, v in enumerate(sum(df.isnull().values)) if v]
            info["1D"]["General information"]["Nulls present in these columns: "] = ", ".join(null_columns)

        info["2D"] = {}
        info["2D"]["Most frequent values in non numerical columns"] = {}
        for i in np.setdiff1d(df.columns, numerical.columns):
            info["2D"]["Most frequent values in non numerical columns"][i] = (df.groupby(i)
                                                                    .count()
                                                                    .max(axis=1)
                                                                    .sort_values(ascending=False)
                                                                    .head(10)
                                                                    .to_dict())

        # Information gathering about numerical columns
        info["2D"]["Information about numerical columns"] = {}
        for c in numerical:
            col = numerical[c]
            info["2D"]["Information about numerical columns"][c] = {"Mean": col["mean"],
                                    "Standard deviation": col["std"],
                                    "Minimal value": col["min"],
                                    "Maximal value": col["max"]
                                    }

    # Information gathering for .txt files
    else:
        file = open(path, "r")
        txt = file.read()
        info["1D"] = {}
        info["1D"]["General information"] = {}
        info["1D"]["General information"]["Number of characters: "] = len(txt)
        info["1D"]["General information"]["Number of words: "] = len(txt.split(" "))
        info["1D"]["General information"]["Number of sentences: "] = len(re.split("\. |! |\? ", txt))
        mails = []
        websites = []
        for i in txt.split(" "):
            if "@" in i:
                mails.append(i)
            elif "https://" in i or "http://" in i or "www." in i:
                websites.append(i)
        info["1D"]["General information"]["Emails found in text: "] = ", ".join(mails)
        info["1D"]["General information"]["Websites found in text: "] = ", ".join(websites)
        file.close()
    return info

if __name__ == "__main__":
    app.run(host="0.0.0.0")