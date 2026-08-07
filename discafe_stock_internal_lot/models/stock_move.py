# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models
from odoo.tools import float_compare


class StockMove(models.Model):
    _inherit = "stock.move"

    allowed_restrict_lot_ids = fields.Many2many(
        "stock.lot",
        string="Allowed Restrict Lots",
        compute="_compute_allowed_restrict_lot_ids",
        help="Lots selectable in the 'Restrict Lot' column of this move. For "
        "internal transfers only lots of the move product with available "
        "stock in the source location are offered; for other transfers the "
        "list is limited to lots of the move product.",
    )

    @api.depends("product_id", "location_id", "picking_code")
    def _compute_allowed_restrict_lot_ids(self):
        Quant = self.env["stock.quant"]
        Lot = self.env["stock.lot"]
        for move in self:
            if not move.product_id:
                move.allowed_restrict_lot_ids = False
                continue
            if move.picking_code == "internal" and move.location_id:
                rounding = move.product_id.uom_id.rounding
                quants = Quant.search([
                    ("product_id", "=", move.product_id.id),
                    ("location_id", "child_of", move.location_id.id),
                    ("lot_id", "!=", False),
                ])
                lots = quants.filtered(
                    lambda quant: float_compare(
                        quant.available_quantity, 0, precision_rounding=rounding
                    ) > 0
                ).mapped("lot_id")
            else:
                lots = Lot.search([("product_id", "=", move.product_id.id)])
            move.allowed_restrict_lot_ids = lots
