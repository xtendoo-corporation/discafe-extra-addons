from odoo import models, fields, api


class Pricelist(models.Model):
    _inherit = "product.pricelist"

    campaign_ids = fields.Many2many(
        comodel_name='sale.campaign',
        relation='sale_campaign_pricelist_rel',
        column1='pricelist_id',
        column2='campaign_id',
        string='Campaigns')

    @api.model
    def get_promotions(self, partner_id):
        self.ensure_one()
        promotions = self.env['sale.promotion']
        today = fields.Date.context_today(self)
        partner = partner_id if getattr(partner_id, '_name', False) == 'res.partner' else self.env['res.partner'].browse(partner_id)
        for campaign in self._get_campaigns(today, partner):
            promotions |= campaign.promotion_ids.filtered(
                lambda p: p.active and
                (not p.start_date or p.start_date <= today) and
                (not p.end_date or p.end_date >= today)
            )
        return promotions

    def _get_campaigns(self, today, partner_id):
        self.ensure_one()
        return self.campaign_ids.filtered(
            lambda c: c.active and
            (not c.start_date or c.start_date <= today) and
            (not c.end_date or c.end_date >= today) and
            (c.all_partners or partner_id in c.partner_ids)
        )
