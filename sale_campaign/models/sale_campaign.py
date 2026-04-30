from odoo import models, fields


class SaleCampaign(models.Model):
    _name = 'sale.campaign'
    _description = 'Sale Campaign'

    name = fields.Char(
        string='Name',
        required=True)
    promotion_ids = fields.Many2many(
        comodel_name='sale.promotion',
        relation='sale_campaign_promotion_rel',
        column1='campaign_id',
        column2='promotion_id',
        string='Promotions')
    start_date = fields.Date(
        string='Start Date')
    end_date = fields.Date(
        string='End Date')
    all_partners = fields.Boolean(
        string='All partners',
        default=True)
    partner_ids = fields.Many2many(
        comodel_name='res.partner',
        string='Partners')
    pricelist_ids = fields.Many2many(
        comodel_name='product.pricelist',
        relation='sale_campaign_pricelist_rel',
        column1='campaign_id',
        column2='pricelist_id',
        string='Pricelists')
    active = fields.Boolean(
        string='Active',
        default=True)
