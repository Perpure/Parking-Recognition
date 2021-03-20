from flask import Flask, url_for, render_template
import sources
app = Flask('parking-recognition', template_folder="jinja_templates")


@app.route('/')
def start():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)

