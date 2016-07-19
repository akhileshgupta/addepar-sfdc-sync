import os
import psycopg2
import requests
import urlparse
from flask import Flask, render_template

app = Flask(__name__)
app.config.from_object('config.Config')
app.config.update(dict(ADDEPAR_KEY=os.environ['ADDEPAR_KEY'],
                       ADDEPAR_SECRET=os.environ['ADDEPAR_SECRET']))

dburl = urlparse.urlparse(os.environ.get('DATABASE_URL'))
db = 'dbname={} user={} password={} host={}'.format(dburl.path[1:], dburl.username,
                                                    dburl.password, dburl.hostname)
conn = psycopg2.connect(db)


@app.route('/')
def hello():
    return 'Hello World!'


@app.route('/accounts')
def accounts():
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM salesforce.account;")
        accounts = cur.fetchall()
        cur.close()

        return render_template('accounts.html', accounts=accounts)
    except Exception as e:
        return str(e)


@app.route('/config')
def config():
    return str(dict(app.config))


@app.route('/addepar')
def addepar():
    """Query the V1 Portfolio API and return the results"""
    portfolio_url = '{}/api/v1/portfolio/views/{}/results'.format(app.config['FIRM_URL'],
                                                                  app.config['ACCOUNTS_VIEW'])
    auth = (app.config['ADDEPAR_KEY'], app.config['ADDEPAR_SECRET'])
    print(auth)
    params = {
        'portfolio_type': 'firm',
        'portfolio_id': app.config['FIRM_ID'],
        'output_type': 'csv',
        'start_date': '2016-06-01',
        'end_date': '2016-06-01'
    }
    data = requests.get(portfolio_url,
                        auth=auth,
                        params=params)

    print('headers', dict(data.request.headers))
    print('url', data.request.url)
    return data.text

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
