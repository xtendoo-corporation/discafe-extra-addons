# -*- coding: utf-8 -*-

from odoo import api, models, fields
from odoo.exceptions import ValidationError


class AccountPayment(models.Model):
    _name = "account.payment"
    _inherit = ['account.payment', 'administrator.mixin.rule']

    lock_date = fields.Boolean(
        string="Lock date",
        compute='_compute_lock_date',
        store=False
    )

    @api.depends_context('uid')
    def _compute_lock_date(self):
        """Compute if date is locked based on user permissions"""
        is_not_admin = not self.env.user.has_group('d_hr_administration.administration')
        for record in self:
            record.lock_date = is_not_admin

    def action_cancel(self):
        """Override cancel action to check permissions"""
        if not self.env.user.has_group('d_hr_administration.administration'):
            raise ValidationError("No tiene permisos para cancelar Pagos")
        return super().action_cancel()

    def action_draft(self):
        """Override draft action to check permissions"""
        if not self.env.user.has_group('d_hr_administration.administration'):
            raise ValidationError("No tiene permisos para cambiar a borrador")
        return super().action_draft()
