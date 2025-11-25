# -*- coding: utf-8 -*-

from odoo import api, exceptions, fields, models, _
from odoo.exceptions import ValidationError


class AccountInvoice(models.Model):
    _inherit = "account.move"

    def _get_partner_delivery_zone(self):
        # Verificar si estamos en un contexto web
        if self.env.context.get('is_web_request'):
            # Acceder a request.session solo si estamos en un contexto web
            if 'partner_delivery_zone_id' in self.env.context.get('request', {}).session:
                return self.env.context['request'].session.get('partner_delivery_zone_id')
        # Si no estamos en un contexto web, devolvemos un valor por defecto
        return 0

    delivery_zone_id = fields.Many2one(
        comodel_name='partner.delivery.zone',
        string="Delivery Zone",
        ondelete='restrict',
        required=True,
        index=True,
        default=_get_partner_delivery_zone,
    )


# from odoo import api, exceptions, fields, models, _
# from odoo.http import request
#
# import logging
#
#
# class AccountInvoice(models.Model):
#     _inherit = "account.move"
#
#     def _get_partner_delivery_zone(self):
#         if 'partner_delivery_zone_id' in request.session:
#             return request.session['partner_delivery_zone_id']
#         return 0
#
#     delivery_zone_id = fields.Many2one(
#         comodel_name='partner.delivery.zone',
#         string="Delivery Zone",
#         ondelete='restrict',
#         required=True,
#         index=True,
#         default=_get_partner_delivery_zone,
#     )
