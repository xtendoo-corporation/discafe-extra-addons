# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    # Método para obtener la zona de entrega del partner desde la sesión HTTP
    def _get_partner_delivery_zone(self):
        # Verificamos si estamos en un contexto de solicitud HTTP
        if self.env.context.get('is_web_request'):
            if 'partner_delivery_zone_id' in self.env.context.get('request', {}).session:
                return self.env.context['request'].session.get('partner_delivery_zone_id')
        # Devolvemos un valor por defecto si no estamos en un contexto HTTP
        return 0

    delivery_zone_id = fields.Many2one(
        comodel_name='partner.delivery.zone',
        string="Delivery Zone",
        ondelete='restrict',
        index=True,
        required=True,
        default=_get_partner_delivery_zone,
    )


# from odoo import api, fields, models
# from odoo.http import request
#
#
# class StockPicking(models.Model):
#     _inherit = 'stock.picking'
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
#         index=True,
#         required=True,
#         default=_get_partner_delivery_zone,
#     )
