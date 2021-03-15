from flask import Flask, url_for
app = Flask('parking-recognition')


@app.route('/')
def start():
    return 'HI'


if __name__ == '__main__':
    app.run()
