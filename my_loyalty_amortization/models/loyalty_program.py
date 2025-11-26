# -*- coding: utf-8 -*-

from odoo import fields, models


class LoyaltyProgram(models.Model):
    _inherit = 'loyalty.program'

    amortization = fields.Boolean(
        string="Amortización",
        default=False,
        help="Indica si este programa de fidelidad utiliza amortización. "
             "Este campo solo es relevante para programas de tipo 'Comprar X recibir Y'."
    )

