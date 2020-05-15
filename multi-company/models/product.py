# -*- coding: utf-8 -*-

from odoo import api, models, fields, _

class Product(models.Model):
    _inherit = 'product.template'

    restricted_company_id = fields.Many2one('res.company', string="Restricted Company")