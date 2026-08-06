# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = "sale.order"


    @api.model
    def default_get(self, default_fields):
        fields = super(SaleOrder, self).default_get(default_fields)

        if not self.env.user.warehouse_id:
            raise UserError(_(
                "No tiene un almacén asignado. "
                "Configure el almacén en su ficha de usuario antes de crear un pedido."
            ))

        fields['warehouse_id'] = self.env.user.warehouse_id.id

        return fields
