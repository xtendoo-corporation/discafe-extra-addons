# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class Users(models.Model):
    _name = 'res.users'
    _inherit = ['res.users', 'administrator.mixin.rule']

    administration = fields.Boolean(
        string='Administración',
        default=False,
        help="Indica si el usuario tiene permisos de administración"
    )
