from flask import Blueprint, render_template, redirect, url_for, flash, request
from werkzeug.utils import secure_filename
import os
from config import Config
from utils.helpers import allowed_file, login_required, admin_required
from services.csv_processor import CSVService

upload = Blueprint("upload", __name__, url_prefix="/upload")


@upload.route("", methods=["GET", "POST"])
@login_required
@admin_required
def index():
    if request.method == "POST":
        if "file" not in request.files:
            flash("No file selected", "error")
            return redirect(request.url)

        file = request.files["file"]
        upload_type = request.form.get("upload_type", "players")

        if file.filename == "":
            flash("No file selected", "error")
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
            file.save(filepath)

            if upload_type == "players":
                success, message = CSVService.process_players_csv(filepath)
            else:
                success, message = CSVService.process_matches_csv(filepath)

            os.remove(filepath)

            if success:
                flash(message, "success")
            else:
                flash(message, "error")

            return redirect(url_for("upload.index"))
        else:
            flash("Invalid file type. Please upload a CSV file.", "error")

    return render_template("upload.html")
