# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    partner_id_readonly = fields.Boolean(
        string='Partner id status',
        default=False,
        compute='_compute_partner_id_readonly',
        store=True)

    @api.depends('order_line')
    def _compute_partner_id_readonly(self):
        for order in self:
            order.partner_id_readonly = bool(order.order_line)

    def _get_delivery_zone_id(self):
        try:
            from odoo.http import request
            if request and request.session and 'partner_delivery_zone_id' in request.session:
                return request.session['partner_delivery_zone_id']
        except Exception:
            pass
        return False

    def _get_next_partner(self):
        zone_id = self._get_delivery_zone_id()
        return self.env['delivery.zone.partner.line'].get_next_partner_not_visited_today(zone_id)

    delivery_zone_id = fields.Many2one(
        comodel_name='partner.delivery.zone',
        string="Delivery Zone",
        ondelete='restrict',
        index=True,
        default=_get_delivery_zone_id,
    )

    @api.model
    def default_get(self, default_fields):
        res = super(SaleOrder, self).default_get(default_fields)
        partner_id = self._get_next_partner()
        if partner_id:
            res['partner_id'] = partner_id.id
        return res

    def button_next_partner(self):
        if self.partner_id_readonly:
            raise ValidationError(_("No puede cambiar de cliente si hay lineas en el pedido"))
        if not self.delivery_zone_id:
            return

        if self.partner_id.id:
            self.env['partner.delivery.zone.visit'].create_if_not_exist(
                self.delivery_zone_id.id, self.partner_id.id
            )

        partner_id = self._get_next_partner()
        if not partner_id:
            raise ValidationError(_("No more partners in this delivery zone"))

        self.partner_id = partner_id

    @api.model
    def create(self, vals):
        if vals.get('delivery_zone_id') and vals.get('partner_id'):
            self.env['partner.delivery.zone.visit'].create_if_not_exist(
                vals['delivery_zone_id'], vals['partner_id']
            )
        return super(SaleOrder, self).create(vals)
