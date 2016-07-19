"""Mappings is an object that goes from table name to mapping object.

Each mapping object has a view name that corresponds to the table, a "columns"
object which maps columns to entries in the CSV and a "constants" object which
maps columns to constant values.
"""
mappings = {
    # 'account': {
    #     'name': 'CLIENTS',
    #     'columns': {},
    #     'constants': {}
    # },
    'finserv__financialaccount__c': {
        'name': 'ACCOUNTS',
        'columns': {
            'name': 'Client',
            'addepar_entity_id__c': 'Client [Entity ID]'
        },
        'constants': {
            'finserv__individualtype__c': 'Individual',
            'recordtypeid': '01236000000NPpsAAG'
        }
    }
    # 'finserv__financialholding__c': {},
    # 'finserv__securities__c': {}
}
