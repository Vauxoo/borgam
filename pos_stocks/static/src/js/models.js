/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : <https://store.webkul.com/license.html/> */

odoo.define('pos_stock.models',function(require) {
    "use strict";
    
    var models = require('point_of_sale.models');
    var core = require('web.core');
    var model_list = models.PosModel.prototype.models
    var SuperOrder = models.Order.prototype;
    var SuperPosModel = models.PosModel.prototype;
    var SuperOrderline = models.Orderline.prototype;
	var rpc = require('web.rpc');
    var product_model = null;
    var _t = core._t;

    models.load_fields('product.product',['qty_available','virtual_available','outgoing_qty','type']);
	models.load_models([{
	label:  'Loading Product Stock',
	loaded: function(self){
        rpc.query({
            model:'pos.config',
            method:'wk_pos_fetch_pos_stock',
            args:[{'wk_stock_type': self.config.wk_stock_type,'wk_hide_out_of_stock':self.config.wk_hide_out_of_stock,'config_id':self.config.id},]
        })
		.then(function(result) {
			self.set({ 'wk_product_qtys': result });
            self.db.wk_product_qtys = result;
			self.db.wk_hide_out_of_stock = self.config.wk_hide_out_of_stock;
		});
	}
	}],{
		'before': 'product.product'
	});

    for(var i = 0,len = model_list.length;i<len;i++){
        if(model_list[i].model == "product.product"){
            product_model = model_list[i];
            break;
        }
    }

      //--Updating product model dictionary--
      var super_product_loaded = product_model.loaded;
      product_model.loaded = function(self,products){
        var product_data = self.db.wk_product_qtys;
        if(self.config.wk_display_stock && self.config.wk_hide_out_of_stock){
            var available_product = [];
            var product_data = self.db.wk_product_qtys;
            var data_list = Object.keys(product_data);
            for(var i = 0,len = products.length; i<len; i++){
                if(data_list.indexOf(products[i].id.toString()) != -1)
                    switch(self.config.wk_stock_type){
                        case'forecasted_qty':
                            if(products[i].virtual_available>0||products[i].type == 'service')
                                available_product.push(products[i]);
                            break;
                        case'virtual_qty':
                            if((products[i].qty_available-products[i].outgoing_qty)>0||products[i].type == 'service')
                                available_product.push(products[i]);
                            break;
                        default:
                            if(products[i].qty_available>0||products[i].type == 'service'){
                                available_product.push(products[i]);
                            }
                    }
            }
            products = available_product;
        }
        self.chrome.wk_change_qty_css();
        super_product_loaded.call(this,self,products);
    };

    models.Order = models.Order.extend({
        add_product: function(product, options){
            var self = this;
            options = options || {};
            // warehouse management compatiblity code start---------------  
            for (var i = 0; i < this.orderlines.length; i++) {
                if(self.orderlines.at(i).product.id == product.id && self.orderlines.at(i).stock_location_id){
                    options.merge = false;
                }
            }
            // warehouse management compatiblity code end---------------
           
            if(!self.pos.config.wk_continous_sale && self.pos.config.wk_display_stock && !self.pos.get_order().is_return_order) {
				var qty_count = 0;
				if(parseInt($("#qty-tag" + product.id).html()))
                    qty_count = parseInt($("#qty-tag" + product.id).html())
				else{
                    var wk_order = self.pos.get('orders');
                    var wk_p_qty = new Array();
                    var qty;
                    var wk_product_obj = self.pos.get('wk_product_qtys');
                    if (wk_order) {
                        for (var i in wk_product_obj)
                            wk_p_qty[i] = self.pos.get('wk_product_qtys')[i];
                        _.each(wk_order.models,function(order){
                            var orderline = order.orderlines.models
                            if(orderline.length > 0)
                                _.each(orderline, function(line){
                                    if(!line.stock_location_id && product.id == line.product.id)
                                        wk_p_qty[line.product.id] = wk_p_qty[line.product.id] - line.quantity;
                                })
                        })
                        qty = wk_p_qty[product.id];
                    }
                    qty_count = qty
                }
                if(qty_count <= self.pos.config.wk_deny_val)
                    self.pos.gui.show_popup('out_of_stock',{
                        'title':  _t("Warning !!!!"),
                        'body': _t("("+product.display_name+")"+self.pos.config.wk_error_msg+"."),
                        'product_id': product.id
                    });
                else 
                    SuperOrder.add_product.call(this, product, options);
            }else 
                SuperOrder.add_product.call(this, product, options);
            if (self.pos.config.wk_display_stock  && !self.is_return_order)
                self.pos.chrome.wk_change_qty_css();
        },
    });

    models.PosModel = models.PosModel.extend({
        push_and_invoice_order: function(order) {
            var self = this;
            if (order != undefined) {
                if(!order.is_return_order){
                    var wk_order_line = order.get_orderlines();
                    for (var j = 0; j < wk_order_line.length; j++) {
                        self.get('wk_product_qtys')[wk_order_line[j].product.id] = self.get('wk_product_qtys')[wk_order_line[j].product.id] - wk_order_line[j].quantity;
                    }
                }else{
                    var wk_order_line = order.get_orderlines();
                    for (var j = 0; j < wk_order_line.length; j++) {
                        self.get('wk_product_qtys')[wk_order_line[j].product.id] = self.get('wk_product_qtys')[wk_order_line[j].product.id] + wk_order_line[j].quantity;
                    }
                }
            }
            var push = SuperPosModel.push_and_invoice_order.call(this, order);
            return push;
        },
        push_order: function(order, opts) {
            var self = this;
            if (order != undefined) {
                if(!order.is_return_order){
                    var wk_order_line = order.get_orderlines();
                    for (var j = 0; j < wk_order_line.length; j++) {
                        if(!wk_order_line[j].stock_location_id)
                            self.get('wk_product_qtys')[wk_order_line[j].product.id] = self.get('wk_product_qtys')[wk_order_line[j].product.id] - wk_order_line[j].quantity;
                    }
                }else{
                    var wk_order_line = order.get_orderlines();
                    for (var j = 0; j < wk_order_line.length; j++) {
                        self.get('wk_product_qtys')[wk_order_line[j].product.id] = self.get('wk_product_qtys')[wk_order_line[j].product.id] + wk_order_line[j].quantity;
                    }
                }
            }
            return SuperPosModel.push_order.call(this, order, opts);
        },
    });
    
    models.NumpadState = models.NumpadState.extend({
        delete_last_char_of_buffer: function() {
            var self = this;
            if(this.get('buffer') === ""){
                if(this.get('mode') === 'quantity')
                    this.trigger('set_value','remove');
                else
                    this.trigger('set_value',this.get('buffer'));
            }else if(this.get('buffer').length >1){
                var newBuffer = this.get('buffer').slice(0,-1) || "";
                this.set({ buffer: newBuffer });
                this.trigger('set_value',this.get('buffer'));
            }
        }
    });
    
    
    models.Orderline = models.Orderline.extend({
        template: 'Orderline',
        initialize: function(attr,options){
            this.option = options;
            this.wk_line_stock_qty = 0.0
            if (options.product)
                this.wk_line_stock_qty=parseInt($("#qty-tag" + options.product.id).html());
            SuperOrderline.initialize.call(this,attr,options);
        },

        set_quantity: function(quantity, keep_price){
            var self = this;
            // -------code for POS Warehouse Management----------------
            if(self.stock_location_id && quantity && quantity!='remove'){
                if(self.pos.get_order() &&  self.pos.get_order().selected_orderline &&  self.pos.get_order().selected_orderline.cid == self.cid){
                    self.pos.gui.show_popup('out_of_stock',{
                        'title':  _t("Warning !!!!"),
                        'body': _t("Selected orderline product have different stock location, you can't update the qty of this orderline"),
                        'product_id': self.product.id
                    });
                    $('.numpad-backspace').trigger("update_buffer");
                    return ;
                }
                else{
                    SuperOrderline.set_quantity.call(this, quantity, keep_price);
                    return;
                }   
            }
            // -------code for POS Warehouse Management----------------
            
            if((!self.pos.config.wk_continous_sale && self.pos.config.wk_display_stock && isNaN(quantity)!=true && quantity!='' && parseFloat(self.wk_line_stock_qty)-parseFloat(quantity)<self.pos.config.wk_deny_val && self.wk_line_stock_qty !=0.0 )){
                self.pos.gui.show_popup('out_of_stock',{
                    'title':  _t("Warning !!!!"),
                    'body': _t("("+this.option.product.display_name+")"+self.pos.config.wk_error_msg+"."),
                    'product_id': this.option.product.id
                });
                $('.numpad-backspace').trigger("update_buffer");
            }
            else{
                var wk_avail_pro = 0;
                if (self.pos.get('selectedOrder')) {
                    var wk_pro_order_line = (self.pos.get('selectedOrder')).get_selected_orderline();
                    if (!self.pos.config.wk_continous_sale && self.pos.config.wk_display_stock && wk_pro_order_line) {
                        var wk_current_qty = parseInt($("#qty-tag" + (wk_pro_order_line.product.id)).html());
                        if (quantity == '' || quantity == 'remove')
                            wk_avail_pro = wk_current_qty + wk_pro_order_line;
                        else
                            wk_avail_pro = wk_current_qty + wk_pro_order_line - quantity;
                        if (wk_avail_pro < self.pos.config.wk_deny_val && (!(quantity == '' || quantity == 'remove'))) {
                            self.pos.gui.show_popup('out_of_stock',{
                                'title':  _t("Warning !!!!"),
                                'body': _t("("+wk_pro_order_line.product.display_name+")"+self.pos.config.wk_error_msg+"."),
                                'product_id':wk_pro_order_line.product.id
                            });
                        }else
                            SuperOrderline.set_quantity.call(this, quantity, keep_price);
                    }else
                        SuperOrderline.set_quantity.call(this, quantity, keep_price);
                    if(self.pos.config.wk_display_stock) 
                        self.pos.chrome.wk_change_qty_css();
                }
                else
                    SuperOrderline.set_quantity.call(this, quantity, keep_price);
            }
        },
    });
});