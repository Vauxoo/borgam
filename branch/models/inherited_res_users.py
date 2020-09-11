# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.model
    def _check_branch_ids(self):
        print(self , "sssssssssssssssssssssssssssssssss",self.branch_ids)
        return [('id','in',self.branch_ids.ids)]

    @api.model
    def _check_allowed_branch_ids(self):
        print(self ,"jjjjjjjjjjjjjjjjjjjjjjjjjjjjjj",self.company_ids)
        return [('company_id','in',self.company_ids.ids)]


    @api.constrains('branch_id', 'branch_ids')
    def _check_branch(self):
        if any(user.branch_id not in user.branch_ids for user in self):
            raise ValidationError(_('The chosen branch is not in the allowed branch for this user'))

    branch_ids = fields.Many2many('res.branch',string="Allowed Branch")
    branch_id = fields.Many2one('res.branch', string= 'Branch')

    def write(self, values):
        if 'branch_id' in values or 'branch_ids' in values:
            self.env['ir.model.access'].call_cache_clearing_methods()
            self.env['ir.rule'].clear_caches()
            self.has_group.clear_cache(self)
        user = super(ResUsers, self).write(values)
        return user
