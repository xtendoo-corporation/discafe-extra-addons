from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    partner_id_readonly = fields.Boolean(
        string='Partner id status',
        default=False,
        compute='_compute_partner_id_readonly',
        store=True)

    @api.depends('order_line')
    def _compute_partner_id_readonly(self):
        for order in self:
            # No bloquear el cliente en pedidos aún no guardados: si no, el
            # alta de un pedido nuevo con líneas en un solo guardado pierde
            # el partner_id (el widget omite los campos readonly al crear).
            order.partner_id_readonly = bool(order.order_line) and not isinstance(order.id, models.NewId)

    # @api.onchange('order_line')
    # def _onchange_order_lines(self):
    #     print("*"*50)
    #     print("order_line", self.order_line)
    #     print("*"*50)
    #     self._compute_partner_id_readonly

    def apply_promotions_multi(self):
        for order in self:
            order.apply_promotions()

    def apply_promotions(self):
        self.ensure_one()
        lines_to_reset = self.order_line.filtered(
            lambda l: not l.display_type and not l.promotion and l.promotion_ids
        )
        # Comentario migración Odoo 18: se restauran descuento y precio antes de recalcular para evitar promociones obsoletas.
        lines_to_reset.write({'discount': 0})
        for line in lines_to_reset:
            line._reset_price_unit()
        # Comentario migración Odoo 18: se eliminan líneas promocionales generadas para evitar duplicados al recalcular.
        self.order_line.filtered(lambda l: l.promotion and not l.display_type).unlink()
        self.order_line.filtered(lambda l: not l.display_type).write({'promotion_ids': [(5, 0, 0)]})
        for promotion in self.pricelist_id.get_promotions(self.partner_id):
            order_lines = self.get_keys(promotion)
            # Check promotions
            if order_lines:
                if promotion.mixing_allowed:
                    order_lines.apply_promotions(promotion)
                else:
                    for product_id in order_lines.mapped('product_id.id'):
                        order_lines_by_product = order_lines.filtered(
                            lambda l: l.product_id.id == product_id
                        )
                        order_lines_by_product.apply_promotions(promotion)

    def get_sale_keys(self, apply_on):
        self.ensure_one()
        order_lines = self.order_line.filtered(
            lambda l: not l.display_type and not l.promotion and l.product_id
        )
        if apply_on == 'product_template':
            return order_lines.mapped(
                lambda l: l.product_id.product_tmpl_id.id)
        elif apply_on == 'product_variant':
            return order_lines.mapped(
                lambda l: l.product_id.id)
        elif apply_on == 'product_category':
            return order_lines.mapped(
                lambda l: l.product_id.categ_id.id)
        else:
            return False

    def get_sale_lines_by_keys(self, promotion, keys):
        self.ensure_one()
        order_lines = self.order_line.filtered(
            lambda l: not l.display_type and not l.promotion and l.product_id
        )
        if promotion.apply_on == 'product_template':
            return order_lines.filtered(
                lambda l: l.product_id.product_tmpl_id.id in keys
            )
        elif promotion.apply_on == 'product_variant':
            return order_lines.filtered(
                lambda l: l.product_id.id in keys
            )
        elif promotion.apply_on == 'product_category':
            return order_lines.filtered(
                lambda l: l.product_id.categ_id.id in keys
            )
        else:
            return False

    def get_keys(self, promotion):
        self.ensure_one()
        sale_key_ids = self.get_sale_keys(promotion.apply_on)
        promotion_key_ids = promotion.get_promotion_keys()
        keys = sale_key_ids and promotion_key_ids and \
            list(set(sale_key_ids) & set(promotion_key_ids))
        if keys:
            return self.get_sale_lines_by_keys(promotion, keys)
        else:
            return False
