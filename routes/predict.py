from flask import Blueprint, request, render_template, flash
from services.prediction import PredictionService

predict = Blueprint("predict", __name__, url_prefix="/predict")


@predict.route("", methods=["GET", "POST"])
def index():
    prediction = None
    model_info = PredictionService.get_model_info()

    if request.method == "POST":
        possession = float(request.form.get("possession", 50))
        shots = int(request.form.get("shots", 10))
        shots_on_target = int(request.form.get("shots_on_target", 5))
        corners = int(request.form.get("corners", 5))
        venue = request.form.get("venue", "Home")

        result, error = PredictionService.predict(
            possession, shots, shots_on_target, corners, venue
        )

        if error:
            flash(error, "warning")
        else:
            prediction = result

    return render_template("predict.html", prediction=prediction, model_info=model_info)
