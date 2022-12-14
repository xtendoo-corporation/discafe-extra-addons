# -- coding: utf-8 --


from odoo import api, models, fields
from odoo.exceptions import ValidationError
import logging


class AccountInvoice(models.Model):
    _inherit = ['account.invoice','administrator.mixin.rule']
    _name = 'account.invoice'

    @api.model
    def default_get(self, default_fields):
        """Si el contexto trae el dato 'active_model' y ese model es 'sale_order' eso quiere decir
        que viene de un pedido por tanto lo dejamos pasar
        """
        #logging.info('get')
        #logging.info(self.env.context.get('active_model', ''))
        #logging.info(self.env.context.get('is_sale', ''))
        if self.env.context.get('active_model', '') == 'sale.order' or self.env["res.users"].has_group(
                "d_hr_administration.administration"
            ) or self.env.context.get('is_sale', '') == True:
            return super(AccountInvoice, self).default_get(default_fields)

        raise ValidationError(("You are not allowed to create invoices."))

    @api.multi
    def action_invoice_cancel(self):
        if not self.env.user.administration:
            raise ValidationError(("No tiene permisos para cancelar facturas"))
        return self.filtered(lambda inv: inv.state != 'cancel').action_cancel()
