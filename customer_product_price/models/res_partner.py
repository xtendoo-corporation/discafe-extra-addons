# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # Campo para mostrar el nombre de la lista de tarifas
    pricelist_name = fields.Char(
        string='Nombre Lista de Tarifas',
        compute='_compute_pricelist_name',
        store=False
    )

    @api.depends('property_product_pricelist')
    def _compute_pricelist_name(self):
        for partner in self:
            try:
                if partner.property_product_pricelist:
                    partner.pricelist_name = partner.property_product_pricelist.name or ''
                else:
                    partner.pricelist_name = ''
            except:
                partner.pricelist_name = ''
