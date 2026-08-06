# Copyright 2018 Tecnativa - Sergio Teruel
# Copyright 2020 Xtendoo - Manuel Calero Solís
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models, api
from datetime import datetime, date


class PartnerDeliveryZone(models.Model):
    _inherit = 'partner.delivery.zone'

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

    @api.model
    def get_report_action(self, active_ids):
        action = self.env.ref('xtendoo_partner_delivery_zone.partner_delivery_zone_wizard_action').read()[0]
        action['context'] = self._context
        return action

    def get_quotations_today(self):
        today = date.today()
        return self.env['sale.order'].search(
            [('delivery_zone_id', '=', self.id),
             ('state', '=', 'draft'),
             ('date_order', '>=', datetime.combine(today, datetime.min.time())),
             ('date_order', '<=', datetime.combine(today, datetime.max.time()))]
        )

    def get_orders_today(self):
        today = date.today()
        return self.env['sale.order'].search(
            [('delivery_zone_id', '=', self.id),
             ('state', '!=', 'draft'),
             ('date_order', '>=', datetime.combine(today, datetime.min.time())),
             ('date_order', '<=', datetime.combine(today, datetime.max.time()))]
        )

    def get_pickings_today(self):
        today = date.today()
        return self.env['stock.picking'].search(
            [('delivery_zone_id', '=', self.id),
             ('scheduled_date', '>=', datetime.combine(today, datetime.min.time())),
             ('scheduled_date', '<=', datetime.combine(today, datetime.max.time()))]
        )

    def get_invoices_today(self):
        return self.env['account.move'].search(
            [('delivery_zone_id', '=', self.id),
             ('state', '!=', 'draft'),
             ('invoice_date', '=', date.today())]
        )

    def get_payments_today(self):
        return self.env['account.payment'].search(
            [('delivery_zone_id', '=', self.id),
             ('date', '=', date.today())]
        )
