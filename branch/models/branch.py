# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class ResBranch(models.Model):
	_name = 'res.branch'
	_description = 'Branch'

	name = fields.Char(required=True)
	company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)
	telephone = fields.Char(string='Telephone No')
	address = fields.Text('Address')

	@api.model
	def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
		user_id = self.env['res.users'].browse(self._context.get('uid'))
		if 'allow_branch' in self.env.context:
			args += [('company_id', 'in',user_id.company_ids.ids)]
		# if 'js' in self.env.context:
		# 	args += [('id','in',user_id.branch_ids.ids)]
		if 'allow_branch' not in self.env.context:
			args += [('id','in',user_id.branch_ids.ids),('company_id', 'in',self.env.context.get('allowed_company_ids'))]
		# if 'all_branch' in self.env.context:
		# 	args = []
		return super(ResBranch, self)._name_search(name, args, operator, limit, name_get_uid=name_get_uid) 