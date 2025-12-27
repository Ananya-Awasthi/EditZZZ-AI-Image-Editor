import os
import uuid
import time
from flask import Flask, flash, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
import cv2
import numpy as np

UPLOAD_FOLDER = "uploads"
STATIC_FOLDER = "static"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.secret_key = "super-secret-key"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(STATIC_FOLDER, exist_ok=True)

# ---------------- CLEANUP ----------------
def cleanup_old_files(folder, max_age_seconds=300):
    now = time.time()
    for f in os.listdir(folder):
        path = os.path.join(folder, f)
        if os.path.isfile(path) and now - os.path.getmtime(path) > max_age_seconds:
            try:
                os.remove(path)
            except:
                pass


# ---------------- HELPERS ----------------
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def process_image(filename, operation):
    img_path = os.path.join(UPLOAD_FOLDER, filename)
    img = cv2.imread(img_path)

    if img is None or not operation:
        return None

    name, ext = filename.rsplit(".", 1)

    # ---------- BASIC FILTERS ----------
    if operation == "Grayscale":
        output = f"{name}_gray.{ext}"
        processed = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    elif operation == "Blur":
        output = f"{name}_blur.{ext}"
        processed = cv2.GaussianBlur(img, (15, 15), 0)

    elif operation == "Sharpen":
        output = f"{name}_sharpen.{ext}"
        kernel = np.array([[0, -1, 0],
                           [-1, 5, -1],
                           [0, -1, 0]])
        processed = cv2.filter2D(img, -1, kernel)

    elif operation == "Rotate":
        output = f"{name}_rotate.{ext}"
        h, w = img.shape[:2]
        m = cv2.getRotationMatrix2D((w/2, h/2), 90, 1)
        processed = cv2.warpAffine(img, m, (w, h))

    # ---------- AI FEATURES ----------
    elif operation == "Cartoon":
        output = f"{name}_cartoon.{ext}"

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.medianBlur(gray, 5)

        edges = cv2.adaptiveThreshold(
            gray, 255,
            cv2.ADAPTIVE_THRESH_MEAN_C,
            cv2.THRESH_BINARY,
            9, 9
        )

        color = cv2.bilateralFilter(img, 9, 300, 300)
        processed = cv2.bitwise_and(color, color, mask=edges)

    elif operation == "Edges":
        output = f"{name}_edges.{ext}"
        processed = cv2.Canny(img, 100, 200)

    # ---------- FORMAT ----------
    elif operation in ["PNG", "JPG", "JPEG"]:
        output = f"{name}.{operation.lower()}"
        processed = img

    else:
        return None

    cv2.imwrite(os.path.join(STATIC_FOLDER, output), processed)
    return output


# ---------------- ROUTES ----------------
@app.route("/home")
def home():
    cleanup_old_files(UPLOAD_FOLDER)
    cleanup_old_files(STATIC_FOLDER)
    output_file = request.args.get("output")
    return render_template("index.html", output_file=output_file)


@app.route("/edit", methods=["POST"])
def edit():
    cleanup_old_files(UPLOAD_FOLDER)
    cleanup_old_files(STATIC_FOLDER)

    filter_op = request.form.get("filter")
    format_op = request.form.get("format")
    operation = filter_op if filter_op else format_op

    if not operation:
        flash("Please select a filter or format")
        return redirect(url_for("home"))

    file = request.files.get("file")
    if not file or file.filename == "":
        flash("No file uploaded")
        return redirect(url_for("home"))

    if allowed_file(file.filename):
        filename = f"{uuid.uuid4()}_{secure_filename(file.filename)}"
        path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(path)

        output = process_image(filename, operation)
        if not output:
            flash("Processing failed")
            return redirect(url_for("home"))

        flash(
            f"Image processed successfully! "
            f"<a href='/static/{output}' download>Click here to download</a>"
        )
        return redirect(url_for("home", output=output))

    flash("Invalid file type")
    return redirect(url_for("home"))


@app.route("/resize", methods=["GET", "POST"])
def resize():
    cleanup_old_files(UPLOAD_FOLDER)
    cleanup_old_files(STATIC_FOLDER)

    if request.method == "POST":
        file = request.files.get("file")
        w = request.form.get("width")
        h = request.form.get("height")

        if not file or not w or not h:
            flash("Missing input")
            return redirect(request.url)

        try:
            w, h = int(w), int(h)
        except:
            flash("Invalid dimensions")
            return redirect(request.url)

        filename = f"{uuid.uuid4()}_{secure_filename(file.filename)}"
        path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(path)

        img = cv2.imread(path)
        resized = cv2.resize(img, (w, h))

        out = f"resized_{filename}"
        cv2.imwrite(os.path.join(STATIC_FOLDER, out), resized)

        flash(
            f"Image resized successfully! "
            f"<a href='/static/{out}' download>Click here to download</a>"
        )
        return redirect(url_for("resize"))

    return render_template("resize.html")



if __name__ == "__main__":
    app.run(debug=True, port=5001)

