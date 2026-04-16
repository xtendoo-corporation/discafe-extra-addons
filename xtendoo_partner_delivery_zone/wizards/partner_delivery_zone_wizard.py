# Copyright  2018 Forest and Biomass Romania
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models
from odoo.http import request


class PartnerDeliveryZoneWizard(models.TransientModel):
    _name = "partner.delivery.zone.wizard"
    _description = "Partner Delivery Zone Wizard"

    def _get_partner_delivery_zone(self):
        # In Odoo 18, Many2one defaults must return a recordset or False, not int/0.
        try:
            zone_id = request.session.get("partner_delivery_zone_id")
        except Exception:
            return False

        if not zone_id:
            return False

        zone = self.env["partner.delivery.zone"].browse(zone_id)
        return zone if zone.exists() else False

    partner_delivery_zone = fields.Many2one(
        comodel_name="partner.delivery.zone",
        string="Partner Delivery Zone",
        default=_get_partner_delivery_zone,
    )

    def button_set_partner_delivery_zone(self):
        self.ensure_one()
        request.session["partner_delivery_zone_id"] = self.partner_delivery_zone.id or False
        return {"type": "ir.actions.act_window_close"}
