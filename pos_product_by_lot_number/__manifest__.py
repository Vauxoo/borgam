# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################

{
    'name'          :       "POS Scan Product By Lot/Serial Number",
    'summary'       :       "Allows the POS user to add the products by scanning their Lot/Serial Number.",
    'category'      :       'Point Of Sale',
    'version'       :       '1.0.1',
    'sequence'      :       1,
    'author'        :       'Webkul Software Pvt. Ltd.',
    'license'       :       'Other proprietary',
    'website'       :       'http://www.webkul.com',
    'description'   :       '''Pos add product by lot, Pos add product by serial number, Lot number scanner, Serial number scanner
                                , Scan product by lot number, Scan product by serial number''',
    "live_test_url" :       "http://odoodemo.webkul.com/?module=pos_product_by_lot_number&custom_url=/pos/auto",
    'depends'       :       ['point_of_sale',],
    'data'          :       ['views/templates.xml'],
    'demo'          :       ['data/product_by_lot_demo.xml'],
    'qweb'          :       ['static/src/xml/pos_product_by_lot_number.xml'],
    'images'        :       ['static/description/banner.png'],
    'application'   :       True,
    'installable'   :       True,
    'auto_install'  :       False,
    'price'	        :        69,
    'currency'      :       'EUR',
    'pre_init_hook' :       'pre_init_check',
}
