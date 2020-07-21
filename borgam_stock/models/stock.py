# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def action_done(self):
        res = super(StockPicking, self).action_done()
        if res:
            for picking in self:
                po = self.env['purchase.order'].sudo().search([('partner_ref', '=', self.origin),
                                                          ('partner_id', '=', self.company_id.partner_id.id),
                                                          ('state', '=', 'purchase')], limit=1)
                if po:
                    StockMoveLine = self.env['stock.move.line'].sudo()
                    StockProdLot = self.env['stock.production.lot'].sudo()
                    po_moves = po.order_line.mapped('move_ids').filtered(
                        lambda m: m.state in ['confirmed', 'partially_available', 'assigned'] and \
                                  m.product_id in self.move_line_ids.mapped('product_id'))
                    po_moves._do_unreserve()
                    for move in self.move_line_ids:
                        po_move = po_moves.filtered(
                            lambda l: l.product_id == move.product_id and l.product_uom_qty == move.move_id.product_uom_qty)
                        if po_move:
                            lot = StockProdLot.search(
                                [('name', '=', move.lot_id.name), ('product_id', '=', move.product_id.id),
                                 ('company_id', '=', po.company_id.id)])
                            if not lot:
                                lot = StockProdLot.create({
                                    'name': move.lot_id.name,
                                    'product_id': move.product_id.id,
                                    'company_id': po.company_id.id
                                })
                            po_move_line = StockMoveLine.create({
                                'product_id': move.product_id.id,
                                'picking_id': po_move[0].picking_id.id,
                                'move_id': po_move[0].id,
                                'location_id': po_move[0].location_id.id,
                                'location_dest_id': po_move[0].location_dest_id.id,
                                'lot_name': move.lot_id.name,
                                'lot_id': lot.id,
                                'qty_done': move.qty_done,
                                'product_uom_id': move.product_uom_id.id,
                            })
                    po_moves._recompute_state()
        return res
