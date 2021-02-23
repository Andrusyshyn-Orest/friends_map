from flask import Flask, render_template, request
from tools.friends_map import main

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/build", methods=["POST"])
def register():
    bearer = request.form.get("bearer")
    screen_name = request.form.get("screen_name")
    count = request.form.get("count")
    if not bearer or not screen_name or not count:
        return render_template("failure.html")

    try:
        main(bearer, screen_name, count)
    except KeyError:
        return render_template("failure1.html")
    except ValueError:
        return render_template("failure2.html")

    return render_template("friends_map.html")


if __name__ == "__main__":
    app.run(debug=True)
