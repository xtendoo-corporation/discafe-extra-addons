# -*- coding: utf-8 -*-
from odoo import models, fields, api
import odoo.addons.decimal_precision as dp


class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'

    # Campo para mostrar los clientes asociados a esta tarifa
    customer_ids = fields.Many2many(
        'res.partner',
        compute='_compute_customer_ids',
        string='Clientes',
        store=False
    )

    customer_names = fields.Text(
        string='Nombres de Clientes',
        compute='_compute_customer_ids',
        store=False
    )

    customer_count = fields.Integer(
        string='Número de Clientes',
        compute='_compute_customer_ids',
        store=False
    )

    def _compute_customer_ids(self):
        for pricelist in self:
            # Buscar clientes que tienen esta lista de tarifas
            customers = self.env['res.partner'].search([
                ('property_product_pricelist', '=', pricelist.id),
                ('customer', '=', True)
            ])
            pricelist.customer_ids = customers
            pricelist.customer_names = ', '.join(customers.mapped('name')) if customers else ''
            pricelist.customer_count = len(customers)


class ProductPricelistItem(models.Model):
    _inherit = 'product.pricelist.item'

    # Precio base del producto (precio de venta estándar)
    product_list_price = fields.Float(
        string='Precio Base Producto',
        compute='_compute_product_list_price',
        store=False,
        digits=dp.get_precision('Product Price')
    )

    @api.depends('product_tmpl_id', 'product_id')
    def _compute_product_list_price(self):
        for item in self:
            try:
                if item.product_id:
                    item.product_list_price = item.product_id.list_price or 0.0
                elif item.product_tmpl_id:
                    item.product_list_price = item.product_tmpl_id.list_price or 0.0
                else:
                    item.product_list_price = 0.0
            except Exception as e:
                item.product_list_price = 0.0
