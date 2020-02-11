# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.http import Controller, route, request, Response

class res_branch(models.Model):
	_name = 'res.branch'

	name = fields.Char('Name', required=True)
	address = fields.Text('Address', size=252)
	telephone_no = fields.Char("Telephone No")
	company_id =  fields.Many2one('res.company', 'Company', required=True)


class res_users(models.Model):
	_inherit = 'res.users'

	branch_id = fields.Many2one('res.branch', 'Current Branch')
	branch_ids = fields.Many2many('res.branch', id1='user_id', id2='branch_id',string='Allowed Branches')

	
class pos_session(models.Model):
	_inherit = 'pos.session'

	branch_id = fields.Many2one('res.branch', 'Branch',related='config_id.branch_id')  
 


class pos_config(models.Model):
	_inherit = 'pos.config'

	branch_id = fields.Many2one('res.branch',string='Branch')      


class pos_order(models.Model):
	_inherit = 'pos.order'

	branch_id = fields.Many2one('res.branch', 'Branch',related='config_id.branch_id')

class pos_payment(models.Model):
	_inherit = 'pos.payment'

	branch_id = fields.Many2one('res.branch',related='pos_order_id.branch_id')      

	
class account_bank_statement(models.Model):

	_inherit = 'account.bank.statement'

	branch_id = fields.Many2one('res.branch', 'Branch',related='pos_session_id.branch_id')


class account_bank_statement_line(models.Model):

	_inherit = 'account.bank.statement.line'

	branch_id = fields.Many2one('res.branch', 'Branch',related='statement_id.branch_id')





# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
