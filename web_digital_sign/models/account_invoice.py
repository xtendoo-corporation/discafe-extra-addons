# See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class AccountMove(models.Model):
    _inherit = 'account.move'

    digital_signature = fields.Binary(string='Digital signature')
