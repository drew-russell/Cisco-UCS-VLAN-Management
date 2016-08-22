"""
A web interface built on Flask and the Cisco UCS Python SDK that has the
following basic functionality:

- Connect to a UCSM domain
- View and Add VLANs
- Add a VLAN to a vNIC

The web UI currently has little to none error handling in place so proceed
accordingly.

"""

from flask import Flask, render_template, request, redirect, url_for


app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():

    index.button_text = "Default"

    if request.method == "POST":

        index.button_text = request.form["button_text"]

        return redirect(url_for('button'))

    return render_template('index.html')


@app.route('/button', methods=['GET', 'POST'])
def button():

    if request.method == "POST":

        return redirect(url_for('index'))

    return render_template('button.html', button_text=index.button_text)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
