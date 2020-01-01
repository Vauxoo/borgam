odoo.define('tis_pos_default_customer.default_customer', function (require) {
"use strict";

var models = require('point_of_sale.models');
var screens = require('point_of_sale.screens');

    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({
        initialize: function(attributes,options){
            var result = _super_order.initialize.apply(this,arguments);
            var client = this.get('client')
            if(client == null){
                var client_obj = this.pos.db.get_partner_by_id(this.pos.config.default_customer[0]);
                this.set('client',client_obj);
            }
            return result;
            
        },
    });

    
});

