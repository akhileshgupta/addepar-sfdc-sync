import arrow
import csv
import os
import psycopg2
import requests
import schedule
import six
import time
import urlparse

# from flask import Flask
from config import config
from mappings import mappings

dburl = urlparse.urlparse(os.environ.get('DATABASE_URL'))
db = 'dbname={} user={} password={} host={}'.format(dburl.path[1:], dburl.username,
                                                    dburl.password, dburl.hostname)
conn = psycopg2.connect(db)
auth = (os.environ['ADDEPAR_KEY'], os.environ['ADDEPAR_SECRET'])


def today():
    """Return today's date (Pacific time zone) as YYYY-MM-DD"""
    return arrow.utcnow().to('US/Pacific').format('YYYY-MM-DD')


def get_csv(view_id):
    """Query the V1 Portfolio API and return the results as a CSV DictReader."""
    portfolio_url = '{}/api/v1/portfolio/views/{}/results'.format(config['FIRM_URL'], view_id)
    firm_id = config['FIRM_ID']
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

    csvdata = data.text[3:].splitlines()
    return csv.DictReader(csvdata)


def gen_sql_string(table, dbcols, unique):
    """Generates a Postgres UPSERT statement with the appropriate number of %s"""
    percents = ','.join(['%s' for _ in range(len(dbcols))])
    dbcolstr = ','.join(dbcols)

    return "INSERT INTO {} ({}) VALUES ({}) ON CONFLICT ({}) DO UPDATE SET ({}) = ({})"\
           .format(table, dbcolstr, percents, unique, dbcolstr, percents)


def handle_num(value):
    """Converts an empty string to None"""
    return value if value else None


def format_data(obj, col, numeric):
    """Format a column based on if its numeric or not. Also has a hack for custom CUSIP"""
    value = obj[col]
    if col in numeric:
        return handle_num(value)
    elif col == 'finserv__cusip__c':
        return None if len(value) > 9 else value
    else:
        return value


def work():
    print('Beginning work')
    cur = conn.cursor()
    for schema in mappings:
        table = schema['table']
        name = schema['name']
        columns = schema['columns']
        constants = schema['constants']
        numeric = schema['numeric']
        unique = schema['unique']

        view_id = config[name + '_VIEW']
        csv = get_csv(view_id)

        insert_obj = [{key: row[col] for key, col in six.iteritems(columns)} for row in csv]
        dbcols = insert_obj[0].keys() + constants.keys()
        sql_string = gen_sql_string(table, dbcols, unique)

        for obj in insert_obj:
            obj.update(constants)

            sql_data = [format_data(obj, col, numeric) for col in dbcols]
            sql_data = sql_data + sql_data

            cur.execute(sql_string, sql_data)

    conn.commit()
    cur.close()
    print('Completed work!')


def drop_trigger_log():
    print('Dropping trigger log')
    cur = conn.cursor()
    for table in config['TRIGGER_TABLES']:
        sql_string = "TRUNCATE TABLE {}".format(table)

        cur.execute(sql_string)

    conn.commit()
    cur.close()
    print('Completed dropping triggers')


"""Start the scheduled job"""
if __name__ == '__main__':
    # app = Flask(__name__)
    # port = int(os.environ.get('PORT', 5000))
    # app.run(host='0.0.0.0', port=port)

    schedule.every().hour.do(work)
    schedule.every(6).hour.do(drop_trigger_log)

    first = True
    while True:
        if first:
            print('Entered while loop')
        first = False
        schedule.run_pending()
        time.sleep(60)
