# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = "sale.order"


    @api.model
    def default_get(self, default_fields):
        result = super().default_get(default_fields)

        if not self.env.user.warehouse_id:
            raise UserError(_(
                "No tiene un almacén asignado. "
                "Configure el almacén en su ficha de usuario antes de crear un pedido."
            ))

        return result

    @api.depends('user_id', 'company_id')
    def _compute_warehouse_id(self):
        # El almacén depende del usuario conectado, no del comercial ni del cliente.
        user_warehouse = self.env.user.warehouse_id
        remaining = self.env['sale.order']
        for order in self:
            editable = order.state in ('draft', 'sent') or not order.ids
            if user_warehouse and user_warehouse.company_id == order.company_id and editable:
                order.warehouse_id = user_warehouse
            else:
                remaining |= order
        if remaining:
            super(SaleOrder, remaining)._compute_warehouse_id()
