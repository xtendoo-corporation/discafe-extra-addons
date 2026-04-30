from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    promotion_ids = fields.Many2many(
        comodel_name='sale.promotion',
        relation='product_template_sale_promotion_rel',
        column1='product_tmpl_id',
        column2='promotion_id',
        string='Promotions')
