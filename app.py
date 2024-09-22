from flask import Flask, render_template, request
from localdata import *

app = Flask(__name__)

@app.route('/')
def index():
    rows = filter_localdata('','')
    page_count = 20
    return render_template('index.html', page_count=page_count, page_number=1, rows=rows)

@app.route('/page/<int:page_number>')
def page_view(page_number):
    location = request.args.get('location', u"경기도")
    page_count, rows = paginate_localdata(int(page_number), location)
    return render_template('index.html', page_count=page_count, page_number=page_number, rows=rows)

@app.route('/update-data')
def update_data():
    start = request.args.get('start', '')
    end = request.args.get('end', '')
    location = request.args.get('location', u"경기도")
    page_number = int(request.args.get('page', '1'))
    #print(f"start={start}, end={end}, location={location}, page={page_number}")
    page_count, rows = paginate_localdata(int(page_number), location)
    return render_template('update-data.html', page_count=page_count, page_number=page_number, rows=rows)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

