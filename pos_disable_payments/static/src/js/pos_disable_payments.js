// pos_disable_payments js
odoo.define('pos_disable_payments.pos_disable_payments', function(require) {
	"use strict";

	var models = require('point_of_sale.models');
	var screens = require('point_of_sale.screens');
	var core = require('web.core');
	var gui = require('point_of_sale.gui');
	var popups = require('point_of_sale.popups');
	var QWeb = core.qweb;
	var session = require('web.session');
	var rpc = require('web.rpc');
	var chrome = require('point_of_sale.chrome');
	var _t = core._t;

	var _super_posmodel = models.PosModel.prototype;
	models.PosModel = models.PosModel.extend({
		initialize: function (session, attributes) {
			var self = this;
			models.load_fields('res.users',['is_allow_payments','is_allow_discount','is_allow_qty','is_edit_price','is_allow_remove_orderline']);
			models.load_fields('hr.employee',['is_allow_payments','is_allow_discount','is_allow_qty','is_edit_price','is_allow_remove_orderline']);
			_super_posmodel.initialize.apply(this, arguments);
		},
	})

	chrome.UsernameWidget.include({
		click_username: function(){
			if(!this.pos.config.module_pos_hr) { return; }
			var self = this;
			this.gui.select_employee({
				'security':     true,
				'current_employee': this.pos.get_cashier(),
				'title':      _t('Change Cashier'),
			}).then(function(employee){
				self.pos.set_cashier(employee);
				self.ProductScreenWidget = new screens.ProductScreenWidget(self,{});
				self.ProductScreenWidget.check_access();
				self.chrome.widget.username.renderElement();
				self.renderElement();

			});
		},
	});

	screens.ProductScreenWidget.include({

		show: function() {
			var self = this;
			self.check_access();
			this._super();
		},

		check_access: function() {
			var self = this;
			var cashier = this.pos.get_cashier();
			var user = this.pos.user;
			if (cashier.user_id != false ){
				this.pos.users.some(function(user) {
					if (user.id === cashier.user_id[0]) {
						cashier.is_allow_payments = user.is_allow_payments;
						cashier.is_allow_discount = user.is_allow_qty;
						cashier.is_allow_qty = user.is_allow_discount;
						cashier.is_edit_price = user.is_edit_price;
						cashier.is_allow_remove_orderline = user.is_allow_remove_orderline;
						return true;
					}
					return false;
				});
			}

			if (cashier.is_allow_payments == true) {
				$('.button.pay').show();
			}
			else{
				$('.button.pay').hide();
			}
			if (cashier.is_allow_qty == true) {
				$('.mode-button.qty.selected-mode').show();
			}
			else{
				$('.mode-button.qty.selected-mode').hide();
			}
			if (cashier.is_allow_discount == true) {
				$('.mode-button.disc').show();
			}
			else{
				$('.mode-button.disc').hide();
			}
			if (cashier.is_edit_price == true) {
				$('.mode-button.price').show();
			}
			else{
				$('.mode-button.price').hide();
			}
			if (cashier.is_allow_remove_orderline == true) {
				$('.input-button.numpad-backspace').show();
			}
			else{
				$('.input-button.numpad-backspace').hide();
			}
		},
	});

});
