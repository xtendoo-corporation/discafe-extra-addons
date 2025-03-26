# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    #quitar, va en sale_campaign
    partner_id_readonly = fields.Boolean(
        string='Partner id status',
        default=False,
        compute='_compute_partner_id_readonly',
        store=True)

    @api.depends('order_line')
    def _compute_partner_id_readonly(self):
        for order in self:
            order.partner_id_readonly = bool(order.order_line)

    # Método para obtener la zona de entrega desde la sesión HTTP
    def _get_delivery_zone_id(self):
        # Usamos 'request' solo si estamos en el contexto de HTTP
        if self.env.context.get('is_web_request'):
            if 'partner_delivery_zone_id' in self.env.context.get('request', {}).session:
                return self.env.context['request'].session.get('partner_delivery_zone_id')
        return 0

    def _get_next_partner(self):
        zone_id = self._get_delivery_zone_id()
        return self.env['delivery.zone.partner.line'].get_next_partner_not_visited_today(zone_id)

    delivery_zone_id = fields.Many2one(
        comodel_name='partner.delivery.zone',
        string="Delivery Zone",
        ondelete='restrict',
        index=True,
        required=True,
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

        # registrar la visita
        if self.partner_id.id:
            self.env['partner.delivery.zone.visit'].create_if_not_exist(self.delivery_zone_id.id, self.partner_id.id)

        # obtener el siguiente cliente
        partner_id = self._get_next_partner()
        if not partner_id:
            raise ValidationError(_("No more partners in this delivery zone"))

        self.partner_id = partner_id
        self.onchange_partner_id()

    @api.model
    def create(self, vals):
        self.env['partner.delivery.zone.visit'].create_if_not_exist(vals['delivery_zone_id'], vals['partner_id'])
        return super(SaleOrder, self).create(vals)



# from odoo import api, fields, models, _
# from odoo.http import request
# from odoo.exceptions import ValidationError
#
#
# class SaleOrder(models.Model):
#     _inherit = 'sale.order'
#
#     #quitar, va en sale_campaign
#     partner_id_readonly = fields.Boolean(
#         string='Partner id status',
#         default=False,
#         compute='_compute_partner_id_readonly',
#         store=True)
#
#     @api.depends('order_line')
#     def _compute_partner_id_readonly(self):
#         for order in self:
#             order.partner_id_readonly = bool(order.order_line)
#
#     def _get_delivery_zone_id(self):
#         if 'partner_delivery_zone_id' in request.session:
#             return request.session['partner_delivery_zone_id']
#         return 0
#
#     def _get_next_partner(self):
#         zone_id = self._get_delivery_zone_id()
#         return self.env['delivery.zone.partner.line'].get_next_partner_not_visited_today(zone_id)
#
#     delivery_zone_id = fields.Many2one(
#         comodel_name='partner.delivery.zone',
#         string="Delivery Zone",
#         ondelete='restrict',
#         index=True,
#         required=True,
#         default=_get_delivery_zone_id,
#     )
#
#     @api.model
#     def default_get(self, default_fields):
#         res = super(SaleOrder, self).default_get(default_fields)
#         partner_id = self._get_next_partner()
#         if partner_id:
#             res['partner_id'] = partner_id.id
#         return res
#
#
#     def button_next_partner(self):
#         if self.partner_id_readonly:
#             raise ValidationError(_("No puede cambiar de cliente si hay lineas en el pedido"))
#         if not self.delivery_zone_id:
#             return
#
#         # register the visit
#         if self.partner_id.id:
#             self.env['partner.delivery.zone.visit'].create_if_not_exist(self.delivery_zone_id.id, self.partner_id.id)
#
#         # get next partner
#         partner_id = self._get_next_partner()
#         if not partner_id:
#             raise ValidationError(_("No more partners in this delivery zone"))
#
#         self.partner_id = partner_id
#         self.onchange_partner_id()
#
#     @api.model
#     def create(self, vals):
#         self.env['partner.delivery.zone.visit'].create_if_not_exist(vals['delivery_zone_id'], vals['partner_id'])
#         return super(SaleOrder, self).create(vals)
#
#
