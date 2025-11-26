# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _name = 'product.template'
    _inherit = ['product.template', 'administrator.mixin.rule']
