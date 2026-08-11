# -*- coding: utf-8 -*-

from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = "account.move"

    def _get_delivery_zone_id_from_session(self):
        try:
            from odoo.http import request
            if request and request.session and 'partner_delivery_zone_id' in request.session:
                print("Encuentra", request.session['partner_delivery_zone_id'])
                return request.session['partner_delivery_zone_id']
        except Exception:
            pass
        print("NO")
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
        print("*"*50)
        print("PASA")
        print("*"*50)
        # La zona la fija la ruta que el usuario tiene seleccionada en la
        # sesión; si no hay ruta activa se usa la zona del cliente (estándar).
        session_zone = self._get_delivery_zone_id_from_session()
        print("session_zone", session_zone)
        for move in self:
            print("Factura")
            if session_zone:
                move.delivery_zone_id = session_zone
                print("move.delivery_zone_id: ", move.delivery_zone_id)
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
