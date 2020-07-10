# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.tools import pycompat
from odoo.tools.float_utils import float_is_zero, float_compare
from odoo.exceptions import UserError

class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    branch_id = fields.Many2one('res.branch', string='Branch')  
    
    @api.model 
    def default_get(self, flds): 
        result = super(MrpBom, self).default_get(flds)
        user_obj = self.env['res.users']
        branch_id = user_obj.browse(self.env.user.id).branch_id.id
        result['branch_id'] = branch_id
        return result  

class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    branch_id = fields.Many2one('res.branch', string='Branch' , related="bom_id.branch_id")


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    branch_id = fields.Many2one('res.branch', string='Branch')  

    @api.model 
    def default_get(self, flds): 
        result = super(MrpProduction, self).default_get(flds)
        user_obj = self.env['res.users']
        branch_id = user_obj.browse(self.env.user.id).branch_id.id
        result['branch_id'] = branch_id
        return result      
    
    @api.onchange('product_id', 'picking_type_id', 'company_id')
    def onchange_product_id(self):
        """ Finds UoM of changed product. """
        if not self.product_id:
            self.bom_id = False
        else:
            bom = self.env['mrp.bom']._bom_find(product=self.product_id, picking_type=self.picking_type_id, company_id=self.company_id.id)
            if bom.type == 'normal':
                self.bom_id = bom.id
                self.branch_id = bom.branch_id.id
            else:
                self.bom_id = False
            self.product_uom_id = self.product_id.uom_id.id
            return {'domain': {'product_uom_id': [('category_id', '=', self.product_id.uom_id.category_id.id)]}}        

    

    @api.onchange('branch_id')
    def onchange_branch_id(self):
        for i in self.move_raw_ids:
            i.update({
                'branch_id' : self.branch_id.id
                })
        

class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    branch_id = fields.Many2one('res.branch', string='Branch')  
    
    @api.model 
    def default_get(self, flds): 
        result = super(MrpWorkorder, self).default_get(flds)
        user_obj = self.env['res.users']
        branch_id = user_obj.browse(self.env.user.id).branch_id.id
        result['branch_id'] = branch_id
        return result

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    branch_id = fields.Many2one('res.branch', string='Branch' , related = "move_id.branch_id" , store = True) 

                    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
