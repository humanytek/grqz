# Copyright 2018 Vauxoo (https://www.vauxoo.com) <info@vauxoo.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': "MRP II",
    'summary': """
    """,
    'author': "Vauxoo",
    'category': 'Manufacturing',
    'version': '11.0.1.0.0',
    'license': "LGPL-3",
    'depends': ['mrp_workorder', 'sale', 'product_compromise'],
    'data': [
        'views/mrp_ii_view.xml',
        'views/stock_view.xml'
    ],
    'demo': [
    ],
    'installable': True,
}
