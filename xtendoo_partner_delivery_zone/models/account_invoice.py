# -*- coding: utf-8 -*-

from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = "account.move"

    def _get_partner_delivery_zone(self):
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
        required=True,
        index=True,
        default=_get_partner_delivery_zone,
    )
