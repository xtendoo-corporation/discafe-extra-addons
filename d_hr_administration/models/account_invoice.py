# -- coding: utf-8 --


from odoo import api, models, fields
from odoo.exceptions import ValidationError
import logging


class AccountMove(models.Model):
    _inherit = ['account.move','administrator.mixin.rule']
    _name = 'account.move'

    @api.model
    def default_get(self, default_fields):
        """Si el contexto trae el dato 'active_model' y ese model es 'sale_order' eso quiere decir
        que viene de un pedido por tanto lo dejamos pasar
        """
        if self.env["res.users"].has_group(
                "d_hr_administration.administration"
            ):
            return super(AccountMove, self).default_get(default_fields)
        if self.env.context.get('params'):
            if self.env.context.get('params').get('model') == 'sale.order' or self.env.context.get('params').get('is_sale') == True:
                return super(AccountMove, self).default_get(default_fields)
        raise ValidationError(("You are not allowed to create invoices."))


    def action_invoice_cancel(self):
        if not self.env.user.administration:
            raise ValidationError(("No tiene permisos para cancelar facturas"))
        return self.filtered(lambda inv: inv.state != 'cancel').action_cancel()
