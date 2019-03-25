# pylint: disable=manifest-required-author
# Copyright 2017 Humanytek.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': "Product Supply",
    'summary': """
    """,
    'author': "Humanytek",
    'website': "http://www.humanytek.com",
    'license': 'AGPL-3',
    'category': 'Manufacturing',
    'version': '11.0.1.0.0',
    'depends': [
        'mrp',
        'product_brand'],
    'data': [
        'report/product_supply_report.xml',
        'report/product_supply_report_template.xml',
        'views/stock_view.xml',
        'wizard/product_supply_view.xml',
    ],
    'demo': [
    ],
    'installable': True,
}
