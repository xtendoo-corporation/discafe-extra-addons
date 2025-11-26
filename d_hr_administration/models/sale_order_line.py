# -*- coding: utf-8 -*-

from odoo import api, models, fields
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class SaleOrderLine(models.Model):
    _name = 'sale.order.line'
    _inherit = ['sale.order.line', 'administrator.mixin.rule']

    # El campo is_admin ya viene del mixin, no necesitamos redefinirlo
    # Si necesitamos un comportamiento específico podemos sobreescribirlo aquí
