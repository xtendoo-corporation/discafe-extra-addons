# -*- coding: utf-8 -*-

from odoo import api, models, fields
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _name = 'account.move'
    _inherit = ['account.move', 'administrator.mixin.rule']

    @api.model_create_multi
    def create(self, vals_list):
        """
        Bloquear la creación de facturas excepto si:
        - El usuario es administrador
        - La factura viene de un pedido de venta
        """
        # Check if user is administrator
        if self.env.user.has_group('d_hr_administration.administration'):
            return super().create(vals_list)

        # Check if coming from sale order
        context_params = self.env.context.get('params', {})
        if context_params.get('model') == 'sale.order' or context_params.get('is_sale'):
            return super().create(vals_list)

        # Check if it's coming from active_model context
        if self.env.context.get('active_model') == 'sale.order':
            return super().create(vals_list)

        raise ValidationError("No tiene permisos para crear facturas manualmente. Use un pedido de venta.")

    def action_cancel(self):
        """Override cancel action to check permissions"""
        if not self.env.user.has_group('d_hr_administration.administration'):
            raise ValidationError("No tiene permisos para cancelar facturas")
        return super().action_cancel()

    def button_cancel(self):
        """Override button cancel to check permissions"""
        if not self.env.user.has_group('d_hr_administration.administration'):
            raise ValidationError("No tiene permisos para cancelar facturas")
        return super().button_cancel()

    def button_draft(self):
        """Override button draft to check permissions"""
        if not self.env.user.has_group('d_hr_administration.administration'):
            raise ValidationError("No tiene permisos para cambiar a borrador")
        return super().button_draft()
