from flask import Flask, render_template
from localdata import *

app = Flask(__name__)

@app.route('/')
def index():
    rows = filter_localdata('','')
    page_count = 20
    return render_template('index.html', page_count=page_count, page_number=1, rows=rows)

@app.route('/page/<int:page_number>')
def page_view(page_number):
    page_count, rows = paginate_localdata(page_number)
    return render_template('index.html', page_count=page_count, page_number=page_number, rows=rows)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

