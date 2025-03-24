# -- coding: utf-8 --


from odoo import api, models, fields
from odoo.exceptions import ValidationError
import logging


class AccountMoveLine(models.Model):
    _inherit = ['account.move.line','administrator.mixin.rule']
    _name = 'account.move.line'
