# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

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
        index=True,
        required=True,
        default=_get_partner_delivery_zone,
    )
