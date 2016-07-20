"""Mappings is an object that goes from table name to mapping object.

Each mapping object has a view name that corresponds to the table, a "columns" object which maps
columns to entries in the CSV, a "constants" object which maps columns to constant values, a
"numeric" set which contains the fields that need to default to null and a "unique" field which
marks the column that is the unique identifier.

ALERT: BE VERY CAREFUL WHEN EDITING THIS OBJECT. TABLE AND COLUMN NAMES ARE INJECTED INTO SQL
STATEMENTS DIRECTLY. YOU COULD ACCIDENTALLY CREATE A SQL INJECTION!
"""
mappings = {
    'salesforce.account': {
        'name': 'ACCOUNTS',
        'columns': {
            'name': 'Client',
            'addepar_entity_id__c': 'Client [Entity ID]'
        },
        'constants': {
            'finserv__individualtype__c': 'Individual',
            'recordtypeid': '01236000000NPpsAAG'
        },
        'numeric': frozenset(),
        'unique': 'addepar_entity_id__c'
    },
    'salesforce.finserv__financialaccount__c': {
        'name': 'FINANCIAL_ACCOUNTS',
        'columns': {
            'finserv__performanceqtd__c': 'Performance QTD',
            'finserv__financialaccountnumber__c': 'Account Number',
            'finserv__performancemtd__c': 'Performance MTD',
            'finserv__balance__c': 'Balance',
            'name': 'Financial Account',
            'finserv__performance1yr__c': 'Performance 1Yr',
            'finserv__performanceytd__c': 'Performance YTD',
            'finserv__performance3yr__c': 'Performance 3Yr',
            'addepar_entity_id__c': 'Financial Account [Entity ID]',
            'FinServ__PrimaryOwner__r__Addepar_Entity_ID__c': 'Client [Entity ID]',
            'FinServ__ServiceProvider__c': 'Financial Service'
        },
        'constants': {
            'FinServ__Ownership__c': 'Individual',
            'recordtypeid': '01236000000NPpsAAG'
        },
        'numeric': frozenset([
            'finserv__performanceqtd__c',
            'finserv__financialaccountnumber__c',
            'finserv__performancemtd__c',
            'finserv__balance__c',
            'finserv__performance1yr__c',
            'finserv__performanceytd__c',
            'finserv__performance3yr__c',
        ]),
        'unique': 'addepar_entity_id__c'
    },
    'salesforce.finserv__financialholding__c': {
        'name': 'FINANCIAL_HOLDINGS',
        'columns': {
            'finserv__price__c': 'Price',
            'name': 'Security',
            'finserv__securities__r__addepar_entity_id__c': 'Security [Entity ID]',
            'finserv__gainloss__c': 'Gain/Loss',
            'finserv__shares__c': 'Quantity',
            'finserv__marketvalue__c': 'Market Value',
            'finserv__financialaccount__r__addepar_entity_id__c': 'Financial Account [Entity ID]',
            'finserv__assetclass__c': 'Asset Class',
            'finserv__primaryowner__r__addepar_entity_id__c': 'Client [Entity ID]',
            'unfunded_commitments__c': 'Unfunded Commitments',
            'addepar_position_id__c': 'Position [Position ID]',
            'finserv__purchaseprice__c': 'Purchase Price'
        },
        'constants': {},
        'numeric': frozenset([
            'finserv__price__c',
            'finserv__gainloss__c',
            'finserv__shares__c',
            'finserv__marketvalue__c',
            'unfunded_commitments__c',
            'finserv__purchaseprice__c'
        ]),
        'unique': 'addepar_position_id__c'
    },
    'salesforce.finserv__securities__c': {
        'name': 'SECURITIES',
        'columns': {
            'name': 'Ticker Symbol',
            'finserv__cusip__c': 'CUSIP',
            'addepar_entity_id__c': 'Security [Entity ID]',
            'finserv__securityid__c': 'BBGID',
            'finserv__price__c': 'Price',
            'finserv__securitiesname__c': 'Security'
        },
        'constants': {},
        'numeric': frozenset([
            'finserv__price__c'
        ]),
        'unique': 'addepar_entity_id__c'
    }
}
