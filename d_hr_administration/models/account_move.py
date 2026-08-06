# -*- coding: utf-8 -*-

from odoo import api, models, _
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _name = 'account.move'
    _inherit = ['account.move', 'administrator.mixin.rule']

    @api.model_create_multi
    def create(self, vals_list):
        if self.env.user.has_group('d_hr_administration.administration'):
            return super().create(vals_list)
        if self.env.su:
            return super().create(vals_list)

        for vals in vals_list:
            if vals.get('move_type', 'entry') not in ('out_invoice', 'out_refund'):
                continue
            from_sale = (
                self.env.context.get('is_sale')
                or self.env.context.get('active_model') == 'sale.order'
            )
            has_sale_lines = any(
                line_vals.get('sale_line_ids')
                for command, _id, line_vals in (
                    line for line in vals.get('invoice_line_ids', [])
                    if isinstance(line, (list, tuple))
                    and len(line) == 3
                    and isinstance(line[2], dict)
                )
            )
            if not from_sale and not has_sale_lines:
                raise ValidationError(_(
                    "No tiene permisos para crear facturas de cliente "
                    "manualmente. Utilice un pedido de venta."
                ))

        return super().create(vals_list)

    def action_cancel(self):
        if not self.env.user.has_group('d_hr_administration.administration'):
            raise ValidationError(_("No tiene permisos para cancelar facturas"))
        return super().action_cancel()

    def button_cancel(self):
        if not self.env.user.has_group('d_hr_administration.administration'):
            raise ValidationError(_("No tiene permisos para cancelar facturas"))
        return super().button_cancel()

    def button_draft(self):
        if not self.env.user.has_group('d_hr_administration.administration'):
            raise ValidationError(_("No tiene permisos para cambiar a borrador"))
        return super().button_draft()
