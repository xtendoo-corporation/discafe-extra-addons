from odoo import models, fields, api


class SalePromotion(models.Model):
    _name = 'sale.promotion'
    _description = 'Sale Promotion'

    name = fields.Char(
        string='Name')
    campaign_ids = fields.Many2many(
        comodel_name='sale.campaign',
        relation='sale_campaign_promotion_rel',
        column1='promotion_id',
        column2='campaign_id',
        string='Campaigns')
    type = fields.Selection(
        [('discount', 'Discount'),
         ('price_unit', 'Special Price'),
         ('add', 'Add Product'),
         ('discount_last', 'Discount last product')],
        string='Type')
    apply_on = fields.Selection(
        [('product_template', 'Product Template'),
         ('product_variant', 'Product Variant'),
         ('product_category', 'Product Category'),
         ],
        string='Apply on')
    apply_on_product_tmpl_ids = fields.Many2many(
        comodel_name='product.template',
        relation='product_template_sale_promotion_rel',
        column1='sale_promotion_id',
        column2='product_template_id',
        string='Apply On Product Templates')
    apply_on_product_ids = fields.Many2many(
        comodel_name='product.product',
        relation='product_product_sale_promotion_rel',
        column1='sale_promotion_id',
        column2='product_product_id',
        string='Apply On Products')
    apply_on_category_ids = fields.Many2many(
        comodel_name='product.category',
        relation='product_category_sale_promotion_rel',
        column1='sale_promotion_id',
        column2='product_category_id',
        string='Apply On Categories')
    apply_to_same_product = fields.Boolean(
        string='Apply to same product',
        default=True)
    apply_to = fields.Selection(
        [('product_template', 'Product Template'),
         ('product_variant', 'Product Variant'),
         ('product_category', 'Product Category'),
         ],
        string='Apply to')
    apply_to_product_tmpl_ids = fields.Many2many(
        comodel_name='product.template',
        relation='sale_promotion_apply_to_product_tmpl_rel',
        column1='promotion_id',
        column2='product_tmpl_id',
        string='Apply To Product Templates')
    apply_to_product_ids = fields.Many2many(
        comodel_name='product.product',
        relation='sale_promotion_apply_to_product_rel',
        column1='promotion_id',
        column2='product_id',
        string='Apply To Products')
    apply_to_category_ids = fields.Many2many(
        comodel_name='product.category',
        relation='sale_promotion_apply_to_category_rel',
        column1='promotion_id',
        column2='categ_id',
        string='Apply To Categories')
    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product')
    promotion_qty_ids = fields.One2many(
        comodel_name='sale.promotion.qty',
        inverse_name='promotion_id',
        string='Quantities')
    promotion_product_tmpl_ids = fields.Many2many(
        comodel_name='product.template',
        relation='sale_promotion_product_tmpl_rel',
        column1='promotion_id',
        column2='product_tmpl_id',
        string='Promotion Product Templates')
    promotion_product_ids = fields.Many2many(
        comodel_name='product.product',
        relation='sale_promotion_product_rel',
        column1='promotion_id',
        column2='product_id',
        string='Promotion Products')
    promotion_category_ids = fields.Many2many(
        comodel_name='product.category',
        relation='sale_promotion_category_rel',
        column1='promotion_id',
        column2='categ_id',
        string='Promotion Categories')
    active = fields.Boolean(
        string='Active',
        default=True)
    start_date = fields.Date(
        string='Start Date')
    end_date = fields.Date(
        string='End Date')
    force_pricelist_price = fields.Boolean(
        string='Force Pricelist Price')
    mixing_allowed = fields.Boolean(
        string='Mixing Allowed')
    excluding_promotion = fields.Boolean(
        string='Excluding Promotion',
        default=False)
    promotion_product_price = fields.Float(
        string='Precio',
        default=0.00)

    def get_promotion_keys(self):
        self.ensure_one()
        if self.apply_on == 'product_template':
            return self.apply_on_product_tmpl_ids.ids
        elif self.apply_on == 'product_variant':
            return self.apply_on_product_ids.ids
        elif self.apply_on == 'product_category':
            return self.apply_on_category_ids.ids
        return []

    def get_apply_to_order_lines(self, order_lines):
        self.ensure_one()
        if self.apply_to == 'product_template':
            return order_lines.filtered(
                lambda l:
                    l.product_id.product_tmpl_id in
                    self.apply_to_product_tmpl_ids)
        elif self.apply_to == 'product_variant':
            return order_lines.filtered(
                lambda l:
                    l.product_id in
                    self.apply_to_product_ids)
        elif self.apply_to == 'product_category':
            return order_lines.filtered(
                lambda l:
                    l.product_id.categ_id in
                    self.apply_to_category_ids)
        return order_lines.browse()

    def get_value(self, qty):
        self.ensure_one()
        values = self.promotion_qty_ids.filtered(
            lambda s: s.start <= qty
        ).sorted('start').mapped(lambda l: (l.start, l.value))
        # Comentario migración Odoo 18: se usa el tramo máximo aplicable para conservar la promoción más específica.
        return values[-1] if values else (False, False)
