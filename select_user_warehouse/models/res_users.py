
from odoo import fields, models


class Users(models.Model):
    _inherit = "res.users"

    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse')

    def _get_default_warehouse_id(self):
        warehouse = self.warehouse_id
        if warehouse and warehouse.company_id == self.env.company:
            return warehouse
        return super()._get_default_warehouse_id()












