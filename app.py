from flask import Flask, render_template
from localdata import *

app = Flask(__name__)

@app.route('/')
def index():
    #output_file = filter_localdata('','')
    sheet = filter_localdata('','')
    #print(sheet)
    return render_template('index.html', rows=sheet)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

