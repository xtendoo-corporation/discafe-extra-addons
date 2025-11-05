# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # Campo para mostrar el nombre de la lista de tarifas
    pricelist_name = fields.Char(
        string='Nombre Lista de Tarifas',
        compute='_compute_pricelist_name',
        store=False,
        readonly=True
    )

    @api.depends('property_product_pricelist')
    def _compute_pricelist_name(self):
        """Compute pricelist name for export purposes"""
        for partner in self:
            if partner.property_product_pricelist:
                partner.pricelist_name = partner.property_product_pricelist.name
            else:
                partner.pricelist_name = ''
