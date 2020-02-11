# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.


{
    'name': 'POS Multiple Branch in Odoo',
    'version': '13.0.0.0',
    'category': 'Point of Sale',
    'summary': 'Multiple Branch/Unit Operation on Point of Sale for single company',
    "description": """
    odoo Multiple Unit operation management for single company Multiple Branch management for single company 
    odoo multiple operation for single company Branch for POS  point of sales multiple branch branch in pos branch on point of sales
    odoo branching in POS multi company pos odoo point of sales Unit Operation For single company
    odoo Branch Operation for POS multiple branch on POS multiple unit operation for POS branch on POS session
    odoo Branch on POS receipt different unit on POS
    odoo POS Unit Operation For single company
    oodoo POS Multiple operating unit management for single company Multiple pos operation management for single company POS multiple operation for single company.
    odoo multiple Branch for POS multiple operating unit for POS odoo
    odoo multiple unit on POS multiple unit operation for POS branch on POS session Branch on POS receipt
    odoo different unit on POS POS Unit Operation For single company odoo operating unit on POS session operating unit on POS receipt
    odoo different unit operation on POS POS multiple Unit Operation For single company
    """,
    'author': 'BrowseInfo',
    'website': 'http://www.browseinfo.in',
    "price": 39,
    "currency": 'EUR',
    'depends': ['base','sale','point_of_sale'],
    'data': [
                'security/branch_security.xml',
                'security/ir.model.access.csv',
                'views/pos_view.xml'
            ],
    'qweb': [
                'static/src/xml/pos.xml',
            ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'live_test_url':'https://youtu.be/jMg67ck2VZA',
    "images":['static/description/Banner.png'],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
