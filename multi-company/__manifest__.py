# -*- coding: utf-8 -*-
{
    'name': "Pastelerias: Multi-company record rule",
    'summary': """
       modify multi-company rule for current product template
    """,

    'description': """
        Task ID: 2243417 - AAL
1. create a M2O field restricted_company_id on product.template
2. modify multi-company rule for current product template so that if this restricted_company_id 
    is set on a product.template and user switches to that specified company, they won't see this product.

    """,

    'author': "Odoo PS-US",
    'website': "http://www.odoo.com",
    'license': 'OEEL-1',

    'category': 'Custom Development',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['product'],

    # always loaded
    'data': [
        'data/rules.xml',
        'views/product_template_inherit.xml'
    ],

}