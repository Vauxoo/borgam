# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import SUPERUSER_ID
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.http import request
from odoo.tools import float_is_zero
import pytz



class pos_session(models.Model):
    _inherit = 'pos.session'

    @api.model
    def create(self,vals):
        res = super(pos_session, self).create(vals)
        user_pool = self.env['res.users']
        if 'config_id' in vals:
            config_id = self.env['pos.config'].browse(vals.get('config_id'))
            if config_id.pos_branch_id:
                res.branch_id = config_id.pos_branch_id.id
            else:
                res.branch_id = user_pool.browse(self.env.uid).branch_id.id  or False    
        else:
            res.branch_id = user_pool.browse(self.env.uid).branch_id.id  or False
        return res

    branch_id = fields.Many2one('res.branch', 'Branch')  


    def _create_account_move(self):
        """ Create account.move and account.move.line records for this session.

        Side-effects include:
            - setting self.move_id to the created account.move record
            - creating and validating account.bank.statement for cash payments
            - reconciling cash receivable lines, invoice receivable lines and stock output lines
        """
        journal = self.config_id.journal_id
        # Passing default_journal_id for the calculation of default currency of account move
        # See _get_default_currency in the account/account_move.py.
        account_move = self.env['account.move'].with_context(default_journal_id=journal.id).create({
            'journal_id': journal.id,
            'date': fields.Date.context_today(self),
            'ref': self.name,
            'branch_id' : self.config_id.pos_branch_id.id
        })
        self.write({'move_id': account_move.id})

        data = {}
        data = self._accumulate_amounts(data)
        data = self._create_non_reconciliable_move_lines(data)
        data = self._create_cash_statement_lines_and_cash_move_lines(data)
        data = self._create_invoice_receivable_lines(data)
        data = self._create_stock_output_lines(data)
        data = self._create_extra_move_lines(data)
        data = self._reconcile_account_move_lines(data)

class pos_config(models.Model):
    _inherit = 'pos.config'

    @api.model
    def _allow_branch_list(self):
        return [('id','in',self.env.user.branch_ids.ids),('company_id','=',self.env.company.id)]


    pos_branch_id = fields.Many2one('res.branch',string='Branch' , domain = _allow_branch_list)


class pos_order(models.Model):
    _inherit = 'pos.order'

    @api.model
    def _payment_fields(self, order, ui_paymentline):
        payment_date = ui_paymentline['name']
        payment_date = fields.Date.context_today(self, fields.Datetime.from_string(payment_date))
        return {
            'amount': ui_paymentline['amount'] or 0.0,
            'payment_date': payment_date,
            'payment_method_id': ui_paymentline['payment_method_id'],
            'card_type': ui_paymentline.get('card_type'),
            'transaction_id': ui_paymentline.get('transaction_id'),
            'branch_id':order.branch_id.id,
            'pos_order_id': order.id,
        }


    def _process_payment_lines(self, pos_order, order, pos_session, draft):
        prec_acc = order.pricelist_id.currency_id.decimal_places

        order_bank_statement_lines= self.env['pos.payment'].search([('pos_order_id', '=', order.id)])
        order_bank_statement_lines.unlink()
        for payments in pos_order['statement_ids']:
            if not float_is_zero(payments[2]['amount'], precision_digits=prec_acc):
                order.add_payment(self._payment_fields(order, payments[2]))

        order.amount_paid = sum(order.payment_ids.mapped('amount'))

        if not draft and not float_is_zero(pos_order['amount_return'], prec_acc):
            cash_payment_method = pos_session.payment_method_ids.filtered('is_cash_count')[:1]
            if not cash_payment_method:
                raise UserError(_("No cash statement found for this session. Unable to record returned cash."))
            return_payment_vals = {
                'name': _('return'),
                'pos_order_id': order.id,
                'branch_id' : order.branch_id.id,
                'amount': -pos_order['amount_return'],
                'payment_date': fields.Date.context_today(self),
                'payment_method_id': cash_payment_method.id,
            }
            order.add_payment(return_payment_vals)
            
    def _create_account_move_line(self, session=None, move=None):
        def _flatten_tax_and_children(taxes, group_done=None):
            children = self.env['account.tax']
            if group_done is None:
                group_done = set()
            for tax in taxes.filtered(lambda t: t.amount_type == 'group'):
                if tax.id not in group_done:
                    group_done.add(tax.id)
                    children |= _flatten_tax_and_children(tax.children_tax_ids, group_done)
            return taxes + children

        IrProperty = self.env['ir.property']
        ResPartner = self.env['res.partner']

        if session and not all(session.id == order.session_id.id for order in self):
            raise UserError(_('Selected orders do not have the same session!'))

        grouped_data = {}
        have_to_group_by = session and session.config_id.group_by or False
        rounding_method = session and session.config_id.company_id.tax_calculation_rounding_method

        def add_anglosaxon_lines(grouped_data):
            Product = self.env['product.product']
            Analytic = self.env['account.analytic.account']
            for product_key in list(grouped_data.keys()):
                if product_key[0] == "product":
                    line = grouped_data[product_key][0]
                    product = Product.browse(line['product_id'])
                    # In the SO part, the entries will be inverted by function compute_invoice_totals
                    price_unit = self._get_pos_anglo_saxon_price_unit(product, line['partner_id'], line['quantity'])
                    account_analytic = Analytic.browse(line.get('analytic_account_id'))
                    res = Product._anglo_saxon_sale_move_lines(
                        line['name'], product, product.uom_id, line['quantity'], price_unit,
                            fiscal_position=order.fiscal_position_id,
                            account_analytic=account_analytic)
                    if res:
                        line1, line2 = res
                        line1 = Product._convert_prepared_anglosaxon_line(line1, order.partner_id)
                        insert_data('counter_part', {
                            'name': line1['name'],
                            'account_id': line1['account_id'],
                            'credit': line1['credit'] or 0.0,
                            'debit': line1['debit'] or 0.0,
                            'partner_id': line1['partner_id']

                        })

                        line2 = Product._convert_prepared_anglosaxon_line(line2, order.partner_id)
                        insert_data('counter_part', {
                            'name': line2['name'],
                            'account_id': line2['account_id'],
                            'credit': line2['credit'] or 0.0,
                            'debit': line2['debit'] or 0.0,
                            'partner_id': line2['partner_id']
                        })

        for order in self.filtered(lambda o: not o.account_move or o.state == 'paid'):
            current_company = order.sale_journal.company_id
            account_def = IrProperty.get(
                'property_account_receivable_id', 'res.partner')
            order_account = order.partner_id.property_account_receivable_id.id or account_def and account_def.id
            partner_id = ResPartner._find_accounting_partner(order.partner_id).id or False
            if move is None:
                # Create an entry for the sale
                journal_id = self.env['ir.config_parameter'].sudo().get_param(
                    'pos.closing.journal_id_%s' % current_company.id, default=order.sale_journal.id)
                move = self._create_account_move(
                    order.session_id.start_at, order.name, int(journal_id), order.company_id.id)

            def insert_data(data_type, values):
                # if have_to_group_by:
                values.update({
                    'partner_id': partner_id,
                    'move_id': move.id,
                })

                key = self._get_account_move_line_group_data_type_key(data_type, values, {'rounding_method': rounding_method})
                if not key:
                    return

                grouped_data.setdefault(key, [])

                if have_to_group_by:
                    if not grouped_data[key]:
                        grouped_data[key].append(values)
                    else:
                        current_value = grouped_data[key][0]
                        current_value['quantity'] = current_value.get('quantity', 0.0) + values.get('quantity', 0.0)
                        current_value['credit'] = current_value.get('credit', 0.0) + values.get('credit', 0.0)
                        current_value['debit'] = current_value.get('debit', 0.0) + values.get('debit', 0.0)
                        if key[0] == 'tax' and rounding_method == 'round_globally':
                            if current_value['debit'] - current_value['credit'] > 0:
                                current_value['debit'] = current_value['debit'] - current_value['credit']
                                current_value['credit'] = 0
                            else:
                                current_value['credit'] = current_value['credit'] - current_value['debit']
                                current_value['debit'] = 0

                else:
                    grouped_data[key].append(values)

            assert order.lines, _('The POS order must have lines when calling this method')
            # Create an move for each order line
            cur = order.pricelist_id.currency_id
            for line in order.lines:
                amount = line.price_subtotal

                # Search for the income account
                if line.product_id.property_account_income_id.id:
                    income_account = line.product_id.property_account_income_id.id
                elif line.product_id.categ_id.property_account_income_categ_id.id:
                    income_account = line.product_id.categ_id.property_account_income_categ_id.id
                else:
                    raise UserError(_('Please define income account for this product: "%s" (id:%d).') % (line.product_id.name, line.product_id.id))

                name = line.product_id.name
                if line.notice:
                    # add discount reason in move
                    name = name + ' (' + line.notice + ')'

                base_line_tax_ids = _flatten_tax_and_children(line.tax_ids_after_fiscal_position).filtered(lambda tax: tax.type_tax_use in ['sale', 'none'])
                insert_data('product', {
                    'name': name,
                    'quantity': line.qty,
                    'product_id': line.product_id.id,
                    'account_id': income_account,
                    'analytic_account_id': self._prepare_analytic_account(line),
                    'credit': ((amount > 0) and amount) or 0.0,
                    'debit': ((amount < 0) and -amount) or 0.0,
                    'tax_ids': [(6, 0, base_line_tax_ids.ids)],
                    'partner_id': partner_id
                })

                # Create the tax lines
                taxes = line.tax_ids_after_fiscal_position.filtered(lambda t: t.company_id.id == current_company.id)
                if not taxes:
                    continue
                price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                for tax in taxes.compute_all(price, cur, line.qty)['taxes']:
                    insert_data('tax', {
                        'name': _('Tax') + ' ' + tax['name'],
                        'product_id': line.product_id.id,
                        'quantity': line.qty,
                        'account_id': tax['account_id'] or income_account,
                        'credit': ((tax['amount'] > 0) and tax['amount']) or 0.0,
                        'debit': ((tax['amount'] < 0) and -tax['amount']) or 0.0,
                        'tax_line_id': tax['id'],
                        'partner_id': partner_id,
                        'order_id': order.id
                    })

            # round tax lines per order
            if rounding_method == 'round_globally':
                for group_key, group_value in grouped_data.items():
                    if group_key[0] == 'tax':
                        for line in group_value:
                            line['credit'] = cur.round(line['credit'])
                            line['debit'] = cur.round(line['debit'])

            # counterpart
            insert_data('counter_part', {
                'name': _("Trade Receivables"),  # order.name,
                'account_id': order_account,
                'credit': ((order.amount_total < 0) and -order.amount_total) or 0.0,
                'debit': ((order.amount_total > 0) and order.amount_total) or 0.0,
                'partner_id': partner_id
            })

            order.write({
                'state': 'done', 
                'account_move': move.id
            })

        if self and order.company_id.anglo_saxon_accounting:
            add_anglosaxon_lines(grouped_data)

        all_lines = []
        for group_key, group_data in grouped_data.items():
            for value in group_data:
                all_lines.append((0, 0, value),)
        if move:  # In case no order was changed
            move.branch_id = session.branch_id.id
            move.sudo().write({'line_ids': all_lines})
            for lines in move.line_ids:
                lines.branch_id = session.branch_id.id
            move.sudo().post()
        return True


    def create_picking(self):
        """Create a picking for each order and validate it."""
        Picking = self.env['stock.picking']
        Move = self.env['stock.move']
        StockWarehouse = self.env['stock.warehouse']
        for order in self:
            if not order.lines.filtered(lambda l: l.product_id.type in ['product', 'consu']):
                continue
            address = order.partner_id.address_get(['delivery']) or {}
            picking_type = order.picking_type_id
            return_pick_type = order.picking_type_id.return_picking_type_id or order.picking_type_id
            order_picking = Picking
            return_picking = Picking
            moves = Move
            location_id = picking_type.default_location_src_id.id
            if order.partner_id:
                destination_id = order.partner_id.property_stock_customer.id
            else:
                if (not picking_type) or (not picking_type.default_location_dest_id):
                    customerloc, supplierloc = StockWarehouse._get_partner_locations()
                    destination_id = customerloc.id
                else:
                    destination_id = picking_type.default_location_dest_id.id

            if picking_type:
                message = _("This transfer has been created from the point of sale session: <a href=# data-oe-model=pos.order data-oe-id=%d>%s</a>") % (order.id, order.name)
                picking_vals = {
                    'origin': order.name,
                    'partner_id': address.get('delivery', False),
                    'user_id': False,
                    'date_done': order.date_order,
                    'picking_type_id': picking_type.id,
                    'company_id': order.company_id.id,
                    'move_type': 'direct',
                    'note': order.note or "",
                    'location_id': location_id,
                    'location_dest_id': destination_id,
                    'branch_id': order.branch_id.id,
                }
                pos_qty = any([x.qty > 0 for x in order.lines if x.product_id.type in ['product', 'consu']])
                if pos_qty:
                    order_picking = Picking.create(picking_vals.copy())
                    order_picking.message_post(body=message)
                neg_qty = any([x.qty < 0 for x in order.lines if x.product_id.type in ['product', 'consu']])
                if neg_qty:
                    return_vals = picking_vals.copy()
                    return_vals.update({
                        'location_id': destination_id,
                        'location_dest_id': return_pick_type != picking_type and return_pick_type.default_location_dest_id.id or location_id,
                        'picking_type_id': return_pick_type.id
                    })
                    return_picking = Picking.create(return_vals)
                    return_picking.message_post(body=message)

            for line in order.lines.filtered(lambda l: l.product_id.type in ['product', 'consu'] and not float_is_zero(l.qty, precision_rounding=l.product_id.uom_id.rounding)):
                moves |= Move.create({
                    'name': line.name,
                    'product_uom': line.product_id.uom_id.id,
                    'picking_id': order_picking.id if line.qty >= 0 else return_picking.id,
                    'picking_type_id': picking_type.id if line.qty >= 0 else return_pick_type.id,
                    'product_id': line.product_id.id,
                    'product_uom_qty': abs(line.qty),
                    'state': 'draft',
                    'branch_id': order.branch_id.id,
                    'location_id': location_id if line.qty >= 0 else destination_id,
                    'location_dest_id': destination_id if line.qty >= 0 else return_pick_type != picking_type and return_pick_type.default_location_dest_id.id or location_id,
                })

            order.write({'picking_id': order_picking.id or return_picking.id})

            if return_picking:
                order._force_picking_done(return_picking)
            if order_picking:
                order._force_picking_done(order_picking)

            if moves and not return_picking and not order_picking:
                moves._action_assign()
                moves.filtered(lambda m: m.product_id.tracking == 'none')._action_done()

        return True

    def _prepare_invoice(self):
        return {
            'name': self.name,
            'origin': self.name,
            'branch_id': self.branch_id.id,
            'account_id': self.partner_id.property_account_receivable_id.id,
            'journal_id': self.session_id.config_id.invoice_journal_id.id,
            'company_id': self.company_id.id,
            'type': 'out_invoice',
            'reference': self.name,
            'partner_id': self.partner_id.id,
            'comment': self.note or '',
            'currency_id': self.pricelist_id.currency_id.id,
            'user_id': self.env.uid,
        }
    


    def _prepare_invoice_vals(self):
        self.ensure_one()
        timezone = pytz.timezone(self._context.get('tz') or self.env.user.tz or 'UTC')
        vals = {
            'invoice_payment_ref': self.name,
            'invoice_origin': self.name,
            'journal_id': self.session_id.config_id.invoice_journal_id.id,
            'type': 'out_invoice' if self.amount_total >= 0 else 'out_refund',
            'ref': self.name,
            'partner_id': self.partner_id.id,
            'narration': self.note or '',
            # considering partner's sale pricelist's currency
            'currency_id': self.pricelist_id.currency_id.id,
            'invoice_user_id': self.user_id.id,
            'invoice_date': self.date_order.astimezone(timezone).date(),
            'fiscal_position_id': self.fiscal_position_id.id,
            'branch_id' : self.session_id.branch_id.id,
            'invoice_line_ids': [(0, None, self._prepare_invoice_line(line)) for line in self.lines],
        }
        return vals


    def _create_account_move(self, dt, ref, journal_id, company_id):

        pos_session_obj = self.env['pos.session'].search([('name','=', ref)])
        pos_session_branch_id = pos_session_obj.branch_id.id
        date_tz_user = fields.Datetime.context_timestamp(self, fields.Datetime.from_string(dt))
        date_tz_user = fields.Date.to_string(date_tz_user)
        return self.env['account.move'].sudo().create({'ref': ref, 'journal_id': journal_id, 'date': date_tz_user, 'branch_id': pos_session_branch_id})

    @api.model
    def create(self,vals):
        res = super(pos_order, self).create(vals)
        res.branch_id = res.session_id.branch_id.id
        return res
        
    branch_id = fields.Many2one('res.branch', 'Branch')


class PosPaymentIn(models.Model):
    _inherit = "pos.payment"

    branch_id = fields.Many2one('res.branch', 'Branch')
