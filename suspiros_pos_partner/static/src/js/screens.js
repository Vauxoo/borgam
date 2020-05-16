odoo.define('suspiros_pos_partner.screens', function (require) {
    "use strict";
    
    var Screens = require('point_of_sale.screens');
    var gui = require('point_of_sale.gui');
    var core = require('web.core');
    var rpc = require('web.rpc');
    var _t = core._t;

    Screens.ClientListScreenWidget.include({
        save_client_details: function(partner) {
            var self = this;

            var fields = {};
            this.$('.client-details-contents .detail').each(function(idx,el){
                if (self.integer_client_details.includes(el.name)){
                    var parsed_value = parseInt(el.value, 10);
                    if (isNaN(parsed_value)){
                        fields[el.name] = false;
                    }
                    else{
                        fields[el.name] = parsed_value
                    }
                }
                else{
                    fields[el.name] = el.value || false;
                }
            });

            if (!fields.name) {
                this.gui.show_popup('error',_t('A Customer Name Is Required'));
                return;
            }

            if (!fields.vat) {
                this.gui.show_popup('error',_t('A Customer Tax ID Is Required'));
                return;
            }

            if (!fields.phone) {
                this.gui.show_popup('error',_t('A Customer Phone Number Is Required'));
                return;
            }

            if (this.uploaded_picture) {
                fields.image_1920 = this.uploaded_picture;
            }

            fields.id = partner.id || false;

            var contents = this.$(".client-details-contents");
            contents.off("click", ".button.save");


            rpc.query({
                    model: 'res.partner',
                    method: 'create_from_ui',
                    args: [fields],
                })
                .then(function(partner_id){
                    self.saved_client_details(partner_id);
                }).catch(function(error){
                    error.event.preventDefault();
                    var error_body = _t('Your Internet connection is probably down.');
                    if (error.message.data) {
                        var except = error.message.data;
                        error_body = except.arguments && except.arguments[0] || except.message || error_body;
                    }
                    self.gui.show_popup('error',{
                        'title': _t('Error: Could not Save Changes'),
                        'body': error_body,
                    });
                    contents.on('click','.button.save',function(){ self.save_client_details(partner); });
                });
        }
    });
});