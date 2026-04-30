# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.fields import Command
from odoo.tests import common, tagged


@tagged('post_install', '-at_install', 'sale_campaign')
class TestSalePromotion(common.TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.uom_unit = cls.env.ref('uom.product_uom_unit')
        cls.currency = cls.env.company.currency_id
        cls.partner = cls.env['res.partner'].create({'name': 'Partner Included'})
        cls.partner_exclude = cls.env['res.partner'].create({'name': 'Partner Excluded'})
        cls.pricelist = cls.env['product.pricelist'].create({
            'name': 'Sale Campaign Pricelist',
            'currency_id': cls.currency.id,
        })

    @classmethod
    def _create_category(cls, name):
        return cls.env['product.category'].create({'name': name})

    @classmethod
    def _create_product(cls, name, price, categ):
        return cls.env['product.product'].with_context(default_taxes_id=False).create({
            'name': name,
            'type': 'consu',
            'list_price': price,
            'categ_id': categ.id,
            'uom_id': cls.uom_unit.id,
            'uom_po_id': cls.uom_unit.id,
        })

    def _create_campaign(self, name, all_partners=True, partners=None):
        return self.env['sale.campaign'].create({
            'name': name,
            'all_partners': all_partners,
            'partner_ids': [Command.set((partners or self.env['res.partner']).ids)],
            'pricelist_ids': [Command.set(self.pricelist.ids)],
        })

    def _create_promotion(self, campaign, **vals):
        defaults = {
            'name': 'Promotion',
            'campaign_ids': [Command.set(campaign.ids)],
            'apply_to_same_product': True,
            'mixing_allowed': True,
            'excluding_promotion': False,
            'force_pricelist_price': False,
        }
        defaults.update(vals)
        return self.env['sale.promotion'].create(defaults)

    def _create_order(self, partner, lines):
        return self.env['sale.order'].create({
            'partner_id': partner.id,
            'partner_invoice_id': partner.id,
            'partner_shipping_id': partner.id,
            'pricelist_id': self.pricelist.id,
            'order_line': [
                (0, 0, {
                    'name': product.name,
                    'product_id': product.id,
                    'product_uom_qty': qty,
                    'product_uom': product.uom_id.id,
                    'price_unit': product.list_price,
                })
                for product, qty in lines
            ],
        })

    def test_product_template_special_price(self):
        category = self._create_category('Template Price Category')
        product = self._create_product('Template Price Product', 30.75, category)
        campaign = self._create_campaign('Campaign Template Price')
        self._create_promotion(
            campaign,
            name='Template Price Promotion',
            type='price_unit',
            apply_on='product_template',
            apply_on_product_tmpl_ids=[Command.set(product.product_tmpl_id.ids)],
            promotion_qty_ids=[Command.create({'start': 0, 'value': 27.5})],
        )

        order = self._create_order(self.partner, [(product, 1)])
        self.assertEqual(order.order_line.price_unit, 30.75)

        order.apply_promotions()

        self.assertEqual(order.order_line.price_unit, 27.5)

    def test_category_discount_mixing(self):
        category = self._create_category('Mixing Category')
        product_1 = self._create_product('Mixing Product 1', 10.0, category)
        product_2 = self._create_product('Mixing Product 2', 12.0, category)
        campaign = self._create_campaign('Campaign Mixing')
        promotion = self._create_promotion(
            campaign,
            name='Mixing Promotion',
            type='discount',
            apply_on='product_category',
            apply_on_category_ids=[Command.set(category.ids)],
            mixing_allowed=False,
            promotion_qty_ids=[Command.create({'start': 10, 'value': 20})],
        )

        order = self._create_order(self.partner, [(product_1, 5), (product_2, 5)])
        order.apply_promotions()
        self.assertEqual(order.order_line.mapped('discount'), [0, 0])

        promotion.mixing_allowed = True
        order.apply_promotions()
        self.assertEqual(order.order_line.mapped('discount'), [20, 20])

    def test_add_promotion_creates_bonus_line(self):
        category = self._create_category('Bonus Category')
        product = self._create_product('Bonus Product', 15.0, category)
        campaign = self._create_campaign('Campaign Bonus')
        self._create_promotion(
            campaign,
            name='Bonus Promotion',
            type='add',
            apply_on='product_variant',
            apply_on_product_ids=[Command.set(product.ids)],
            promotion_product_price=0.0,
            promotion_qty_ids=[Command.create({'start': 2, 'value': 1})],
        )

        order = self._create_order(self.partner, [(product, 4)])
        order.apply_promotions()

        self.assertEqual(len(order.order_line), 2)
        bonus_line = order.order_line.filtered('promotion')
        self.assertTrue(bonus_line)
        self.assertEqual(bonus_line.product_id, product)
        self.assertEqual(bonus_line.product_uom_qty, 2)
        self.assertEqual(bonus_line.price_unit, 0)
        self.assertTrue(bonus_line.bonus)

    def test_partner_filtering(self):
        category = self._create_category('Partner Category')
        product = self._create_product('Partner Product', 25.0, category)
        campaign = self._create_campaign(
            'Campaign Partner Filter',
            all_partners=False,
            partners=self.partner,
        )
        self._create_promotion(
            campaign,
            name='Partner Discount Promotion',
            type='discount',
            apply_on='product_variant',
            apply_on_product_ids=[Command.set(product.ids)],
            promotion_qty_ids=[Command.create({'start': 0, 'value': 15})],
        )

        included_order = self._create_order(self.partner, [(product, 1)])
        included_order.apply_promotions()
        self.assertEqual(included_order.order_line.discount, 15)

        excluded_order = self._create_order(self.partner_exclude, [(product, 1)])
        excluded_order.apply_promotions()
        self.assertEqual(excluded_order.order_line.discount, 0)

    def test_recalculation_resets_previous_discount(self):
        category = self._create_category('Reset Category')
        product = self._create_product('Reset Product', 40.0, category)
        campaign = self._create_campaign('Campaign Reset')
        promotion = self._create_promotion(
            campaign,
            name='Reset Discount Promotion',
            type='discount',
            apply_on='product_variant',
            apply_on_product_ids=[Command.set(product.ids)],
            promotion_qty_ids=[Command.create({'start': 0, 'value': 10})],
        )

        order = self._create_order(self.partner, [(product, 1)])
        order.apply_promotions()
        self.assertEqual(order.order_line.discount, 10)

        promotion.campaign_ids = [Command.clear()]
        order.apply_promotions()

        self.assertEqual(order.order_line.discount, 0)
        self.assertFalse(order.order_line.promotion_ids)
