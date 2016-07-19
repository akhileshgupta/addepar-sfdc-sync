import csv
import os
import psycopg2
import requests
import six
import urlparse

from flask import Flask
from mappings import mappings

app = Flask(__name__)
app.config.from_object('config.Config')
app.config.update(dict(ADDEPAR_KEY=os.environ['ADDEPAR_KEY'],
                       ADDEPAR_SECRET=os.environ['ADDEPAR_SECRET']))

dburl = urlparse.urlparse(os.environ.get('DATABASE_URL'))
db = 'dbname={} user={} password={} host={}'.format(dburl.path[1:], dburl.username,
                                                    dburl.password, dburl.hostname)
conn = psycopg2.connect(db)
cur = conn.cursor()
auth = (os.environ['ADDEPAR_KEY'], os.environ['ADDEPAR_SECRET'])


def get_csv(view_id):
    """Query the V1 Portfolio API and return the results as a CSV DictReader."""
    portfolio_url = '{}/api/v1/portfolio/views/{}/results'.format(app.config['FIRM_URL'], view_id)
    firm_id = app.config['FIRM_ID']
    params = {
        'portfolio_type': 'firm',
        'portfolio_id': firm_id,
        'output_type': 'csv',
        'start_date': '2016-06-01',
        'end_date': '2016-06-01'
    }

    data = requests.get(portfolio_url,
                        auth=auth,
                        headers={'Addepar-Firm': firm_id},
                        params=params)

    return csv.DictReader(data.text.splitlines())


def mark_unique():
    for table in mappings.keys():
        unique_col = mappings[table]['unique']
        cur.execute('ALTER TABLE % ADD UNIQUE (%)', table, unique_col)


@app.route('/addepar')
def addepar():
    response = ''

    for table in mappings:
        config = mappings[table]
        name = config['name']
        columns = config['columns']
        constants = config['constants']
        view_id = app.config[name + '_VIEW']
        csv = get_csv(view_id)

        insert_obj = {key: csv[col] for key, col in six.iteritems(columns)}
        for obj in insert_obj:
            obj.update(constants)

        response += '{} {}<br>'.format(table, str(insert_obj))

    return response

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
