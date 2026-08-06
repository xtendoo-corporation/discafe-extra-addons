# -*- coding: utf-8 -*-

from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = "account.move"

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
        for move in self:
            move.delivery_zone_id = move.partner_id.delivery_zone_id

    can_edit_delivery_zone = fields.Boolean(
        compute='_compute_can_edit_delivery_zone',
        store=False,
    )

    @api.depends_context('uid')
    def _compute_can_edit_delivery_zone(self):
        can_edit = self.env.user.has_group('d_hr_administration.administration')
        for move in self:
            move.can_edit_delivery_zone = can_edit
