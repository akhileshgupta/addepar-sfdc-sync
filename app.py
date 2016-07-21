import arrow
import csv
import os
import psycopg2
import requests
import six
import threading
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
auth = (os.environ['ADDEPAR_KEY'], os.environ['ADDEPAR_SECRET'])


def today():
    return arrow.utcnow().to('US/Pacific').format('YYYY-MM-DD')


def get_csv(view_id):
    """Query the V1 Portfolio API and return the results as a CSV DictReader."""
    portfolio_url = '{}/api/v1/portfolio/views/{}/results'.format(app.config['FIRM_URL'], view_id)
    firm_id = app.config['FIRM_ID']
    date = today()
    params = {
        'portfolio_type': 'firm',
        'portfolio_id': firm_id,
        'output_type': 'csv',
        'start_date': date,
        'end_date': date
    }

    data = requests.get(portfolio_url,
                        auth=auth,
                        headers={'Addepar-Firm': firm_id},
                        params=params)

    return csv.DictReader(data.text.splitlines())


def gen_sql_string(table, dbcols, unique):
    percents = ','.join(['%s' for _ in range(len(dbcols))])
    dbcolstr = ','.join(dbcols)

    return "INSERT INTO {} ({}) VALUES ({}) ON CONFLICT ({}) DO UPDATE SET ({}) = ({})"\
           .format(table, dbcolstr, percents, unique, dbcolstr, percents)


def handle_num(value):
    return value if value else None


def format_data(obj, col, numeric):
    value = obj[col]
    if col in numeric:
        return handle_num(value)
    elif col == 'finserv__cusip__c':
        return None if len(value) > 9 else value
    else:
        return value


def work():
    cur = conn.cursor()
    for config in mappings:
        table = config['table']
        name = config['name']
        columns = config['columns']
        constants = config['constants']
        numeric = config['numeric']
        unique = config['unique']
        view_id = app.config[name + '_VIEW']
        csv = get_csv(view_id)

        insert_obj = [{key: row[col] for key, col in six.iteritems(columns)} for row in csv]
        dbcols = insert_obj[0].keys() + constants.keys()
        sql_string = gen_sql_string(table, dbcols, unique)

        for obj in insert_obj:
            obj.update(constants)

            sql_data = [format_data(obj, col, numeric) for col in dbcols]
            sql_data = sql_data + sql_data

            statement = cur.mogrify(sql_string, sql_data)
            print(statement)
            cur.execute(sql_string, sql_data)

    conn.commit()
    cur.close()
    print('Completed work!')


@app.route('/addepar')
def addepar():
    t = threading.Thread(target=work)
    t.start()
    return 'Started work, check logs for details'

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
