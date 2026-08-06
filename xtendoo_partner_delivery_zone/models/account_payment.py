# -*- coding: utf-8 -*-

from odoo import api, fields, models


class AccountPayment(models.Model):
    _inherit = "account.payment"

    def _get_delivery_zone_id_from_session(self):
        try:
            from odoo.http import request
            if request and request.session and 'partner_delivery_zone_id' in request.session:
                return request.session['partner_delivery_zone_id']
        except Exception:
            pass
        return False

    delivery_zone_id = fields.Many2one(
        comodel_name='partner.delivery.zone',
        string="Delivery Zone",
        ondelete='restrict',
        index=True,
        compute='_compute_delivery_zone_id',
        store=True,
        readonly=False,
    )

    @api.depends('partner_id')
    def _compute_delivery_zone_id(self):
        session_zone_id = self._get_delivery_zone_id_from_session()
        for payment in self:
            payment.delivery_zone_id = session_zone_id or payment.partner_id.delivery_zone_id

    @api.model_create_multi
    def create(self, vals_list):
        session_zone_id = self._get_delivery_zone_id_from_session()
        if session_zone_id:
            for vals in vals_list:
                vals.setdefault('delivery_zone_id', session_zone_id)
        return super().create(vals_list)
