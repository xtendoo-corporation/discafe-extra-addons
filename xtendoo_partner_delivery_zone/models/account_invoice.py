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
        # La zona la fija la ruta que el usuario tiene seleccionada en la
        # sesión; si no hay ruta activa se usa la zona del cliente (estándar).
        session_zone = self._get_session_delivery_zone()
        for move in self:
            if session_zone and move.state == 'draft':
                move.delivery_zone_id = session_zone
            else:
                move.delivery_zone_id = move.partner_id.delivery_zone_id

    def _get_session_delivery_zone(self):
        zone_id = self.env['sale.order']._get_delivery_zone_id()
        if not zone_id:
            return self.env['partner.delivery.zone']
        zone = self.env['partner.delivery.zone'].browse(zone_id)
        return zone if zone.exists() else self.env['partner.delivery.zone']

    can_edit_delivery_zone = fields.Boolean(
        compute='_compute_can_edit_delivery_zone',
        store=False,
    )

    @api.depends_context('uid')
    def _compute_can_edit_delivery_zone(self):
        can_edit = self.env.user.has_group('d_hr_administration.administration')
        for move in self:
            move.can_edit_delivery_zone = can_edit
