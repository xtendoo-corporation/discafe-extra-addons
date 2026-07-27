# -*- coding: utf-8 -*-

from odoo import api, fields, models


class AccountPayment(models.Model):
    _inherit = "account.payment"

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
        for payment in self:
            payment.delivery_zone_id = payment.partner_id.delivery_zone_id
