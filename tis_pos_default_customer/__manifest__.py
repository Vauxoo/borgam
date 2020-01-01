# -*- coding: utf-8 -*-
# copyright of Technaureus Info Solutions Pvt. Ltd.
# - © Technaureus Info Solutions Pvt. Ltd 2019

{
    'name': 'POS Default Customer',
    'version': '2.0',
    'sequence': 1,
    'category': 'Point of Sale',
    'summary': 'POS default customer',
    'description': """
    pos default customer
""",
    'author': 'Technaureus Info Solutions Pvt. Ltd.',
    'website': 'http://www.technaureus.com/',
    'price': 17,
    'currency': 'EUR',
    'license': 'Other proprietary',
    'depends': ['point_of_sale'],
    'data': [
        'views/views.xml',
        'views/templates.xml'
    ],
    'images': ['images/main_screenshot.png'],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    'live_test_url': 'https://www.youtube.com/watch?v=pmp6QLOq90E'
}
