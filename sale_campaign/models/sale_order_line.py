from odoo import api, models, fields


class OrderLine(models.Model):
    _inherit = "sale.order.line"
    _order = 'sequence'

    bonus = fields.Boolean(
        string='Bonus',
        default=False)
    promotion_ids = fields.Many2many(
        comodel_name='sale.promotion',
        string='Promotion')
    promotion = fields.Boolean(
        string='In promotion',
        default=False)
    parent_id = fields.Many2one('sale.order.line', 'Linea padre')

    def apply_promotions(self, promotion):
        for promo in promotion:
            self.apply_promotion(promo)

    def apply_promotion(self, promotion):
        if promotion.type == 'add':
            self.apply_promotion_add(promotion)
        elif promotion.type in ['discount', 'price_unit']:
            self.apply_promotion_discount_price(
                promotion, promotion.type)
        elif promotion.type == 'discount_last':
            self.apply_promotion_free_last(promotion)

    def apply_promotion_add(self, promotion):
        total_sale_qty = sum(self.mapped('product_uom_qty'))
        (qty, value) = promotion.get_value(total_sale_qty)
        free_qty = qty and value and (total_sale_qty // qty) * value
        if free_qty:
            product_id = self[0].product_id.id if promotion.apply_to_same_product else promotion.product_id.id
            line_to_add = self.sorted('sequence')[-1]
            line_to_add.copy({
                'order_id': line_to_add.order_id.id,
                'sequence': line_to_add.sequence + 1,
                'product_id': product_id,
                'product_uom_qty': free_qty,
                'price_unit': promotion.promotion_product_price,
                'discount': 0,
                'bonus': True,
                'promotion': True,
                'promotion_ids': [(6, 0, promotion.ids)],
                # Comentario migración Odoo 18: la línea promocional se enlaza a la línea origen usada para crearla.
                'parent_id': line_to_add.id,
            })

    def apply_promotion_discount_price(self, promotion, type):
        (qty, value) = promotion.get_value(sum(self.mapped('product_uom_qty')))
        if not value:
            return False
        values = {type: value}
        if promotion.apply_to_same_product:
            order_lines = self
        else:
            order_lines = promotion.get_apply_to_order_lines(
                self.order_id.order_line.filtered(
                    lambda l: not l.display_type and not l.promotion and l.product_id
                )
            )
        for order_line in order_lines:
            if promotion.force_pricelist_price:
                # Comentario migración Odoo 18: se restaura el precio base de tarifa usando la lógica estándar de sale.order.line.
                order_line._reset_price_unit()
            line_values = dict(values)
            line_values.setdefault('promotion_ids', [(4, promotion.id)])
            order_line.write(line_values)

    def apply_promotion_other(self, promotion):
        value = promotion.get_value(sum(self.mapped('product_uom_qty')))
        if value:
            self.order_id.filtered(
                lambda l: (l.product_id == promotion.product_id or
                           (l.product_id.product_tmpl_id == promotion.product_tmpl_id))
            ).write({'discount': promotion.amount})

    def apply_promotion_bonus(self, promotion):
        pass

    def apply_promotion_free_last(self, promotion):
        pass

    def unlink(self):
        # Comentario migración Odoo 18: se eliminan también las líneas hijas promocionales al borrar la línea origen.
        for line in self.filtered(lambda l: not l.promotion):
            son_line = self.env['sale.order.line'].search([('parent_id', '=', line.id)])
            if son_line:
                son_line.unlink()
        return super().unlink()

