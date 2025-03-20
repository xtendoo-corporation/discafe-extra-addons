# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models, api
from datetime import datetime


class PartnerDeliveryZone(models.Model):
    _name = 'partner.delivery.zone'
    _description = 'Partner delivery zone'

    date = datetime.utcnow()

    code = fields.Char()

    name = fields.Char(
        string='Zone',
        required=True,
    )
    partner_zones_ids = fields.One2many(
        'delivery.zone.partner.line',
        'delivery_zone_id',
        string='Partner Zones Line',
        auto_join=True,
    )
    visit_ids = fields.One2many(
        'partner.delivery.zone.visit',
        'delivery_zone_id',
        string='Delivery Zone Visit',
        auto_join=True,
    )
    sale_order_ids = fields.One2many(
        'sale.order',
        'delivery_zone_id',
        string='Delivery Zone',
        auto_join=True,
    )
    active = fields.Boolean(default=True)

    @api.model
    def get_report_action(self, active_ids):
        print("*"*100)
        print("context", self._context)
        action = self.env.ref('xtendoo_partner_delivery_zone.partner_delivery_zone_wizard_action').read()[0]
        action['context'] = self._context
        return action


    def set_values(self):
        super(PartnerDeliveryZone, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param("partner.delivery.zone", self.code or '')


    def get_quotations_today(self):
        return self.env['sale.order'].search(
            [('delivery_zone_id', '=', self.id),
             ('state', '=', 'draft'),
             ('date_order', '>=', datetime.combine(self.date, datetime.min.time())),
             ('date_order', '<=', datetime.combine(self.date, datetime.max.time()))]
        )


    def get_orders_today(self):
        return self.env['sale.order'].search(
            [('delivery_zone_id', '=', self.id),
             ('state', '!=', 'draft'),
             ('date_order', '>=', datetime.combine(self.date, datetime.min.time())),
             ('date_order', '<=', datetime.combine(self.date, datetime.max.time()))]
        )


    def get_pickings_today(self):
        return self.env['stock.picking'].search(
            [('delivery_zone_id', '=', self.id),
             ('scheduled_date', '>=', datetime.combine(self.date, datetime.min.time())),
             ('scheduled_date', '<=', datetime.combine(self.date, datetime.max.time()))]
        )


    def get_invoices_today(self):
        return self.env['account.move'].search(
            [('delivery_zone_id', '=', self.id),
             ('state', '!=', 'draft'),
             ('date_invoice', '=', self.date)]
        )


    def get_payments_today(self):
        return self.env['account.payment'].search(
            [('delivery_zone_id', '=', self.id),
             ('payment_date', '=', self.date)]
        )

