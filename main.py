from flask import Flask, render_template
app = Flask('parking-recognition', template_folder="jinja_templates")


@app.route('/')
def start():
    return render_template("index.html")


if __name__ == '__main__':
    app.run(debug=True)
