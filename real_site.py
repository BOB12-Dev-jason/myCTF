from flask import Flask, render_template, request, jsonify

# flask 객체
app = Flask(__name__)


@app.route("/")
def home():
    return render_template("real_site_index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0")

