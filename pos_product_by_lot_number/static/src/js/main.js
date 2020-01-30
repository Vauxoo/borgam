/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : <https://store.webkul.com/license.html/> */
odoo.define("pos_product_by_lot_number", function(require) {
    "use strict";
  
    var screens = require('point_of_sale.screens');
    var models = require('point_of_sale.models');
    var PopupWidget = require('point_of_sale.popups');
    var rpc = require('web.rpc');
    var gui = require('point_of_sale.gui');
    var SuperOrder = models.Order;
    var SuperPosModel = models.PosModel;
  
  
  
    models.load_models([{
      model: 'stock.production.lot',
      label: 'Serial/Lot Numbers',
      fields: ['name', 'product_id', 'product_qty'],
      loaded: function(self, result) {
        self.db.lot_no = {};
        _.each(result, function(data) {
          self.db.lot_no[data.name] = data;
        });
      }
    }]);
  
  
  
  
    models.PosModel = models.PosModel.extend({
  
      scan_product: function(parsed_code) {
  
        var self = this;
        var result = SuperPosModel.prototype.scan_product.call(this, parsed_code)
        var data = self.db.lot_no[parsed_code.base_code]
        if (!result) {
          if (data) {
            if (data.product_id) {
              var lot_product = data.product_id;
              this.get_order().add_product(self.db.product_by_id[lot_product[0]], {
                scan: true,
                lot_name: parsed_code.base_code
              });
              return true
            }
          }
        }
        return result;
      }
    });
  
    var WkAlertPopUp = PopupWidget.extend({
      template: 'WkAlertPopUp',
    });
    
    gui.define_popup({ name: 'wk_alert_popup', widget: WkAlertPopUp });
  
  
  
    models.Order = models.Order.extend({
  
  
      // add_product_by_type is used to add product
      add_product_by_type: function(product, options) {
  
        if (this._printed) {
          this.destroy();
          return this.pos.get_order().add_product(product, options);
        }
        this.assert_editable();
        options = options || {};
        var attr = JSON.parse(JSON.stringify(product));
        attr.pos = this.pos;
        attr.order = this;
        var line = new models.Orderline({}, {
          pos: this.pos,
          order: this,
          product: product
        });
  
        if (options.quantity !== undefined) {
          line.set_quantity(options.quantity);
        }
  
        if (options.price !== undefined) {
          line.set_unit_price(options.price);
        }
  
        this.fix_tax_included_price(line);
  
        if (options.discount !== undefined) {
          line.set_discount(options.discount);
        }
  
        if (options.extras !== undefined) {
          for (var prop in options.extras) {
            line[prop] = options.extras[prop];
          }
        }
  
        var to_merge_orderline;
        for (var i = 0; i < this.orderlines.length; i++) {
          if (this.orderlines.at(i).can_be_merged_with(line) && options.merge !== false) {
            to_merge_orderline = this.orderlines.at(i);
          }
        }
        if (to_merge_orderline) {
          to_merge_orderline.merge(line);
        } else {
          this.orderlines.add(line);
        }
        this.select_orderline(this.get_last_orderline());
        this.wk_add_lot(options);
  
      },
  
  
  
      product_total_by_lot: function(lot_name) {
        
        var count = 0;
        var lot = this.pos.db.lot_no[lot_name]
        _.each(this.pos.get('orders').models, function(order) {
          _.each(order.get_orderlines(), function(orderline) {
            if (lot && orderline.pack_lot_lines && lot.product_id[0] == orderline.product.id) {
              _.each(orderline.pack_lot_lines.models, function(packlot) {
                if (packlot.attributes["lot_name"] == lot_name) {
                  count += orderline.quantity;
                }
              });
            }
          });
        });
        return count
      },
  
  
      //get_remanining_products is use to calculate the remaining items in lot once the error popup.
      get_remaining_products: function(lot_name) {
  
        var lot = this.pos.db.lot_no[lot_name]
        if (lot) {
          var remaining_qty = lot.product_qty - this.product_total_by_lot(lot_name) + this.pos.get_order().get_selected_orderline().quantity
        }
        return remaining_qty
      },
  
  
      add_product: function(product, options) {
  
        if (options && options.scan) {
  
          var quant = this.product_total_by_lot(options["lot_name"]);
  
          var qty = this.pos.db.lot_no[options["lot_name"]].product_qty;
          var tracking = product.tracking;
          if (tracking == "lot") {
            if (quant < qty) {
              this.add_product_by_type(product, options)
            } else {
              this.pos.gui.show_popup('wk_alert_popup', {
                title: "Lot Is Empty!",
                'body': "The quantity of selected product in lot " + options.lot_name + " is Zero."
              });
            }
  
          } else if (tracking == "serial") {
            if (quant < qty && quant < 1) {
              this.add_product_by_type(product, options)
            } else {
              this.pos.gui.show_popup('wk_alert_popup', {
                title: "Serial Number!",
                'body': "Only one product can be added by using serial number " + options.lot_name + "."
              });
            }
          }
        } else
            return SuperOrder.prototype.add_product.call(this, product, options)
      },
  
  
      //wk_add_lot automatically allots the scanned lot/serial number to the product in orderline
    wk_add_lot: function(options) {
      var order_line = this.get_selected_orderline();
      var pack_lot_lines = order_line.compute_lot_lines();
      if(pack_lot_lines._byId){
        var pack_lot_lines_keys  = Object.keys(pack_lot_lines._byId);
        if(pack_lot_lines_keys && pack_lot_lines_keys.length > 0){
          var cid = pack_lot_lines_keys[pack_lot_lines_keys.length - 1];
          var lot_name = options["lot_name"];
          var pack_line = pack_lot_lines.get({ cid: cid });
          if(pack_line && lot_name)
            pack_line.set_lot_name(lot_name);
        }
        pack_lot_lines.set_quantity_by_lot();
        this.save_to_db();
        order_line.trigger('change', order_line);
      }
    }
    });
  
  
  
  
    screens.OrderWidget.include({
  
      set_value: function(val) {
        var order = this.pos.get_order();
        var selected_orderline = order.get_selected_orderline();
        var lot = this.pos.db.lot_no
        var buffer = this.pos.chrome.screens.products.order_widget.numpad_state
  
        if (selected_orderline) {
          var mode = this.numpad_state.get('mode');
          if (mode === 'quantity') {
            if (selected_orderline.pack_lot_lines._byId && selected_orderline.pack_lot_lines.models[0]) {
              var lot_name = selected_orderline.pack_lot_lines.models[0].attributes["lot_name"];
  
              var is_lot = _.find(lot, function(num) {
                return num.name == lot_name
              });
              var count = order.product_total_by_lot(lot_name) + parseInt(val) - selected_orderline.quantity;
              if (is_lot && (val > lot[lot_name].product_qty || count > lot[lot_name].product_qty)) {
                var value = this.pos.get_order().get_remaining_products(lot_name);
                this.pos.gui.show_popup("wk_alert_popup", {
                  'title': 'Out Of Quantity!',
                  'body': "Maximum products available to add in Lot/Serial Number " + lot_name + " are " + value + "."
                });
                buffer.set('buffer', "")
              } else {
                this._super(val);
              }
  
            } else {
              this._super(val);
            }
          } else {
            this._super(val);
          }
  
        }
      },
  
  
    });
  
  
  
    screens.PaymentScreenWidget.include({
  
      validate_order: function(force_validation) {
        var self = this
        this._super(force_validation)
        var order = this.pos.get_order()
        if(order.finalized)
          this.update_lot();
  
      },
  
      orderline_total_by_lot: function(lot_name) {
        
        var count = 0;
        var lot = this.pos.db.lot_no[lot_name]
        _.each(this.pos.get_order().get_orderlines(), function(orderline) {
          if (lot && orderline.pack_lot_lines && lot.product_id[0] == orderline.product.id) {
            _.each(orderline.pack_lot_lines.models, function(packlot) {
              if (packlot.attributes["lot_name"] == lot_name) {
                count += orderline.quantity;
              }
            });
          }
        });
        return count
      },
  
  
      //update_lot is used to update the lot product quantity according to the validated products by their associated lots
      update_lot: function() {
  
        var self = this;
        this.pos.db.data = self.pos.db.lot_no
        _.each(this.pos.db.data, function(lot) {
          var count = self.orderline_total_by_lot(lot.name);
          lot.product_qty = lot.product_qty - count;
        });
      }
    });
  
  
    var PackLotLinePopupWidget = PopupWidget.extend({
      template: 'PackLotLinePopupWidget',
      events: _.extend({}, PopupWidget.prototype.events, {
        'click .remove-lot': 'remove_lot',
        'keydown': 'add_lot',
        'blur .packlot-line-input': 'lose_input_focus',
        'keyup .packlot-line-input': 'lot_key_press_input',
        'click .packlot-line-input': 'focus_input',
        'click #check_content': 'check_box_element'
      }),
  
      show: function(options) {
  
        var self = this;
        this._super(options);
        this.focus();
        self.index = $(".lot-holder li").length / 2 - 1;
        self.parent = self.$('.lot-holder');
      },
  
      click_cancel: function() {
  
        var self = this
        this._super();
        _.each(this.pos.get_order().get_selected_orderline().pack_lot_lines.models, function(lot) {
          if (lot && lot.error) {
            lot.remove();
            self.pos.get_order().get_selected_orderline().pack_lot_lines.set_quantity_by_lot();
          }
        })
      },
  
      click_confirm: function() {
  
        var self = this;
        var check = 0;
        var pack_lot_lines = this.options.pack_lot_lines;
        self.pos.get_order().get_selected_orderline().count = 0
        self.$('.packlot-line-input').each(function(index, el) {
          var cid = $(el).attr('cid'),
            lot_name = $(el).val();
  
          //to check whether a lot number is in the data or not
  
          if (self.pos.db.lot_no[lot_name] && self.pos.db.lot_no[lot_name].product_id[0] == self.options.order_line.product.id && self.pos.get_order().get_selected_orderline().count == 0 ) {
              check = 1;
          }
          else if (self.pos.db.lot_no[lot_name] && self.pos.db.lot_no[lot_name].product_id[0] == self.options.order_line.product.id && self.pos.get_order().get_selected_orderline().count >= 1) {
              check += 1;
          }
  
          if (check == self.$('.packlot-line-input').length) {
              var cid = $('.packlot-line-input').attr('cid'),
                lot_name = $(el).val();
              var pack_line = pack_lot_lines.get({ cid: cid });
              pack_line.set_lot_name(lot_name);
              pack_lot_lines.remove_empty_model();
              pack_lot_lines.set_quantity_by_lot();
              self.options.order.save_to_db();
              self.options.order_line.trigger('change', self.options.order_line);
              self.gui.close_popup();
  
          } else {                                      //to check via rpc
  
            rpc.query({
                model: 'stock.production.lot',
                method: 'check_lot_by_rpc',
                args: [{
                  'name': lot_name,
                  'product_id': self.options.order_line.product.id
                }]
              })
              .then(function(result) {
  
                var count = 0;
                _.each(pack_lot_lines.models, function(lot) {
                  if (pack_lot_lines && pack_lot_lines.get({ cid: cid }) && pack_lot_lines.get({ cid: cid }).attributes.lot_name == lot.attributes.lot_name) {
                      count += 1;
                  }
                })
                self.pos.get_order().get_selected_orderline().count = count;
                if (!result ||self.pos.get_order().get_selected_orderline().count > 1 ) {            //if result will not be found
                    var selector = "[cid~='" + cid + "']";
                    var pack_line = pack_lot_lines.get({ cid: cid });
                    self.error = true;
                    if(pack_line)
                      pack_line.error = true;
                    self.$(selector).addClass("wk-error");
                    if (self.pos.get_order().get_selected_orderline().count > 1 || self.pos.check ) {
                        self.$(".error-message").hide();
                        self.$(".duplicate-serial").show();
                        self.pos.check = true;
                    } else{
                        self.$(".error-message").show();
                        self.$('.duplicate-serial').hide();
                    }
                }
  
                if (self.$(".checkbox-input").is(':checked') || result) { //condition whether the checkbox is checked or not
  
                    self.$('.packlot-line-input').each(function(index, el) {
                      var cid = $(el).attr('cid'),
                        lot_name = $(el).val();
                      var pack_line = pack_lot_lines.get({ cid: cid });
                      if(pack_line && lot_name)
                        pack_line.set_lot_name(lot_name);
                  });
                  pack_lot_lines.remove_empty_model();
                  pack_lot_lines.set_quantity_by_lot();
                  self.options.order.save_to_db();
                  self.options.order_line.trigger('change', self.options.order_line);
                  self.gui.close_popup();
                  self.error = false;
                  self.pos.check = false;
  
                }
              })
          }
        })
      },
  
      add_lot: function(ev) {
  
        if (ev.keyCode === $.ui.keyCode.ENTER && this.options.order_line.product.tracking == 'serial') {
          var pack_lot_lines = this.options.pack_lot_lines,
            $input = $(ev.target),
            cid = $input.attr('cid'),
            lot_name = $input.val();
          var lot_model = pack_lot_lines.get({ cid: cid });
          lot_model.set_lot_name(lot_name); // First set current model then add new one
          if (!pack_lot_lines.get_empty_model()) {
            var new_lot_model = lot_model.add();
            this.focus_model = new_lot_model;
          }
          pack_lot_lines.set_quantity_by_lot();
          this.renderElement();
          this.focus();
        }
      },
  
      remove_lot: function(ev) {
        var self = this
        var pack_lot_lines = this.options.pack_lot_lines,
          $input = $(ev.target).prev(),
          cid = $input.attr('cid');
        var lot_model = pack_lot_lines.get({ cid: cid });
        lot_model.remove();
        pack_lot_lines.set_quantity_by_lot();
        this.renderElement();
        self.pos.check = false;
  
  
      },
  
      lose_input_focus: function(ev) {
  
        var $input = $(ev.target),
          cid = $input.attr('cid');
        var lot_model = this.options.pack_lot_lines.get({ cid: cid });
        lot_model.set_lot_name($input.val());
  
      },
  
      focus: function() {
  
        this.$("input[autofocus]").focus();
        this.focus_model = false;            // after focus clear focus_model on widget
        this.lot_key_press_input();
  
      },
  
      lot_key_press_input: function(event) {
  
        var self = this;
        var updown_press;
        var all_lots = self.pos.db.lot_no;
        var product_lot = {};
        _.each(all_lots, function(lot) {
          var count = self.pos.get_order().product_total_by_lot(lot.name)
          if (lot.product_id[0] == self.options.order_line.product.id && lot.product_qty > count) {
            var lot_name = lot.name;
            product_lot[lot_name] = lot;
          }
        });
  
  
        $('.lot-holder ul').empty();
        var lot_name = self.$('.packlot-line-input').val();
        self.$('.lot-holder').show();
        if(lot_name)
          lot_name = new RegExp(lot_name.replace(/[^0-9a-z_]/i), 'i');
  
          for (var index in product_lot) {
            if (product_lot[index].name.match(lot_name)) {
              $('.lot-holder ul').append($("<li><span class='lot-name'>" + product_lot[index].name + "</span></li>"));
            }
          }
  
  
        $('.lot-holder ul').show();
        self.$('.lot-holder li').on('click', function() {
          var lot_name = $(this).text();
          self.$(".packlot-line-input").val(lot_name)
          $('.selection-lot').hide();
          $('.packlot-line-input').focus();
        });
  
        if (event && event.which == 38) {
  
          // Up arrow
          self.index--;
          var len = $('.lot-holder li').length;
          if (self.index < $(".lot-holder li").length / 2)
            self.index = len - 1;
          self.parent.scrollTop(36 *(self.index - len/2));
          updown_press = true;
  
        } else if (event && event.which == 40) {
  
          // Down arrow
          self.index++;
          var len = $('.lot-holder li').length
          if (self.index > len - 1)
            self.index = len / 2;
          self.parent.scrollTop(36  * (self.index - len/2 ));
          updown_press = true;
        }
  
        if (updown_press) {
  
          $('.lot-holder li.active').removeClass('active');
          $('.lot-holder li').eq(self.index).addClass('active');
          $('.lot-holder li.active').select();
        }
  
        if (event && event.which == 27) {
  
          // Esc key
          $('.lot-holder ul').hide();
  
        } else if (event && event.which == 13 && self.index >= 0 && $('.lot-holder li').eq(self.index)[0]) {
          
          var selcted_li_lot_id = $('.lot-holder li').eq(self.index)[0].innerText;
          self.$('.packlot-line-input').val(selcted_li_lot_id);
          $('.lot-holder ul').hide();
          self.$('.lot-holder').hide();
          self.index = self.index = $(".lot-holder li").length / 2 - 1;
          self.$('.packlot-line-input').focusout();
        }
  
      },
      focus_input: function() {
        var self = this;
        this.$(".lot-holder").show();
        this.$(".packlot-line-input").removeClass("wk-error")
        self.$(".error-message").hide();
        self.$(".duplicate-serial").hide();
      },
  
      check_box_element: function() {
  
        if (this.$(".checkbox-input").is(':checked'))
          this.$(".checkbox-input").prop('checked', false);
        else
          this.$(".checkbox-input").prop('checked', true);
      }
    });
  
    gui.define_popup({ name: 'packlotline', widget: PackLotLinePopupWidget });
  
  });
  