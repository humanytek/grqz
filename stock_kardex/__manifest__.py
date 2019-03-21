# pylint: disable=manifest-required-author
# Copyright 2017 Humanytek.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': "Kardex",
    'summary': """
    Display the moves of a given product according to the location selected
    """,
    'author': "Humanytek",
    'website': "http://www.humanytek.com",
    'license': "AGPL-3",
    'category': 'Stock',
    'version': '11.0.1.0.0',
    'depends': ['stock'],
    'data': [
        'view/stock_kardex_view.xml',
    ],
    'demo': [
    ],
    'installable': True
}
