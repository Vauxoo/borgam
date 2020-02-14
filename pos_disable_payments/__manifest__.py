# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.


{
    "name" : "Allow/Disable POS Features in Odoo",
    "version" : "13.0.1.0",
    "category" : "Point of Sale",
    'summary': 'This apps helps to Allow and Disable POS Features like Payment, Qty, Discount, Edit Price, Remove Orderline',
    "description": """

    Purpose :-
    Allow/Deny POS Features like Payment Qty Discount Edit Price, Remove Orderline for Particular POS User...!!!
    odoo point of sales disable payment option on POS 
    odoo point of sales disable Discount option on POS
    odoo point of sales disable Edit Price option on POS
    odoo point of sales disable change Price option on POS
    odoo point of sales disable Remove Orderline option on POS
    odoo point of sales disable delete Orderline option on POS
    odoo point of sales disable Remove Order line option on POS
    odoo point of sales disable delete Order line option on POS

    odoo point of sale disable payment option on point of sales 
    odoo point of sale disable Discount option on point of sales
    odoo point of sale disable Edit Price option on point of sales
    odoo point of sale disable change Price option on point of sales
    odoo point of sale disable Remove Orderline option on point of sales
    odoo point of sale disable delete Orderline option on point of sales
    odoo point of sale disable Remove Order line option on point of sales
    odoo point of sale disable delete Order line option on point of sales

    odoo POS disable payment option POS 
    odoo POS disable Discount option POS
    odoo POS disable Edit Price option POS
    odoo POS disable change Price option POS
    odoo POS disable Remove Orderline option POS
    odoo POS disable delete Orderline option POS
    odoo POS disable Remove Order line option POS
    odoo POS disable delete Order line option POS

    odoo point of sale apply and disable payment option point of sale 
    odoo point of sale apply and disable Discount option point of sale
    odoo point of sale apply and disable Edit Price option point of sale
    odoo point of sale apply and disable change Price option point of sale
    odoo point of sale apply and disable Remove Orderline option point of sale
    odoo point of sale apply and disable delete Orderline option point of sale
    odoo point of sale apply and disable Remove Order line option point of sale
    odoo point of sale apply and disable delete Order line option point of sale


    odoo point of sales restrict payment option on POS 
    odoo point of sales restrict Discount option on POS
    odoo point of sales restrict Edit Price option on POS
    odoo point of sales restrict change Price option on POS
    odoo point of sales restrict Remove Orderline option on POS
    odoo point of sales restrict delete Orderline option on POS
    odoo point of sales restrict Remove Order line option on POS
    odoo point of sales restrict delete Order line option on POS

    odoo point of sale restrict payment option on point of sales 
    odoo point of sale restrict Discount option on point of sales
    odoo point of sale restrict Edit Price option on point of sales
    odoo point of sale restrict change Price option on point of sales
    odoo point of sale restrict Remove Orderline option on point of sales
    odoo point of sale restrict delete Orderline option on point of sales
    odoo point of sale restrict Remove Order line option on point of sales
    odoo point of sale restrict delete Order line option on point of sales

    odoo POS restrict payment option POS 
    odoo POS restrict Discount option POS
    odoo POS restrict Edit Price option POS
    odoo POS restrict change Price option POS
    odoo POS restrict Remove Orderline option POS
    odoo POS restrict delete Orderline option POS
    odoo POS restrict Remove Order line option POS
    odoo POS restrict delete Order line option POS

    odoo point of sale apply and restrict payment option point of sale 
    odoo point of sale apply and restrict Discount option point of sale
    odoo point of sale apply and restrict Edit Price option point of sale
    odoo point of sale apply and restrict change Price option point of sale
    odoo point of sale apply and restrict Remove Orderline option point of sale
    odoo point of sale apply and restrict delete Orderline option point of sale
    odoo point of sale apply and restrict Remove Order line option point of sale
    odoo point of sale apply and restrict delete Order line option point of sale



    """,
    "author": "BrowseInfo",
    "website" : "www.browseinfo.in",
    "price": 20,
    "currency": 'EUR',
    "depends" : ['base','sale','point_of_sale','pos_hr'],
    "data": [
        'views/custom_pos_view.xml',
            ],
    'qweb': [
        'static/src/xml/pos_disable_payments.xml',
            ],
    "auto_install": False,
    "installable": True,
    'live_test_url':'https://youtu.be/oOnU8LLLhwA',
    "images":['static/description/Banner.png'],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
