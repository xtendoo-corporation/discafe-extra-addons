# © 2022 Daniel Dominguez <https://xtendoo.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountInvoiceLine(models.Model):
    _inherit = ['account.invoice.line']
    _name = 'account.invoice.line'

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('purchase_price'):
                purchase_price = self.env['product.product'].search(
                    [('id', '=', vals.get("product_id"))]).standard_price
                vals['purchase_price'] = purchase_price
        return super().create(vals_list)
