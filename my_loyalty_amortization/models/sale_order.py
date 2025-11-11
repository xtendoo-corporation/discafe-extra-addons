# -*- coding: utf-8 -*-

from odoo import models
from odoo.fields import Command


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _get_reward_values_product(self, reward, coupon, product=None, **kwargs):
        # Obtener los valores originales
        values = super()._get_reward_values_product(reward, coupon, product=product, **kwargs)

        # Verificar si el programa tiene amortización activada
        if reward.program_id.amortization:
            # Si amortization es True, cambiar el descuento de 100 a 0
            for value_dict in values:
                value_dict['discount'] = 0

        return values

