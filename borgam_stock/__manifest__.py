# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': "BORGAM: Intercompany Stock",
    'version': '1.0',
    'depends': ['purchase_stock', 'sale_stock'],
    'author': 'Odoo Inc',
    'license': 'OEEL-1',
    'mainainer': 'Odoo Inc',
    'category': 'Category',
    'description': """
BORGAM: Intercompany Stock
==========================
- Module that automatically creates move lines for purhcase on sales receipts once the created sales order
  for different company and it's delivery order gets validated.
    """,
    # data files always loaded at installation
    'data': [
    ],
}