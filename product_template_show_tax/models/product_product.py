# -*- coding: utf-8 -*-

from odoo import models, fields


class ProductProduct(models.Model):
    _inherit = 'product.product'

    # Hacer que taxes_id esté disponible en product.product
    # ya que por defecto está en product.template
    taxes_id = fields.Many2many(
        'account.tax',
        related='product_tmpl_id.taxes_id',
        string='Customer Taxes',
        readonly=False,
        store=False
    )

