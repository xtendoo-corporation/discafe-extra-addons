# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from lxml import etree

from odoo import Command
from odoo.tests import tagged

from odoo.addons.base.tests.common import BaseCommon


@tagged("post_install", "-at_install")
class TestPartnerDeliveryZone(BaseCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # select_user_warehouse.default_get exige almacén en el usuario actual.
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.env.user.warehouse_id = cls.warehouse
        cls.delivery_zone_a = cls.env["partner.delivery.zone"].create(
            {"name": "Delivery Zone A", "code": "10"}
        )
        cls.delivery_zone_b = cls.env["partner.delivery.zone"].create(
            {"name": "Delivery Zone B", "code": "20"}
        )
        cls.partner = cls.env["res.partner"].create(
            {"name": "test", "delivery_zone_id": cls.delivery_zone_a.id}
        )
        cls.product = cls.env["product.product"].create(
            {"name": "test", "type": "consu", "tracking": "none"}
        )
        so = cls.env["sale.order"].new(
            {
                "partner_id": cls.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "name": cls.product.name,
                            "product_id": cls.product.id,
                            "product_uom_qty": 10.0,
                            "product_uom": cls.product.uom_id.id,
                            "price_unit": 1000.00,
                        }
                    )
                ],
            }
        )
        cls.order = cls.env["sale.order"].create(so._convert_to_write(so._cache))
        cls.View = cls.env["ir.ui.view"]

    def test_partner_child_propagate(self):
        other_partner = self.env["res.partner"].create(
            {"name": "other partner", "delivery_zone_id": self.delivery_zone_b.id}
        )
        self.order.partner_shipping_id = other_partner
        self.assertEqual(
            self.order.delivery_zone_id, other_partner.delivery_zone_id
        )

    def test_sale_order_confirm(self):
        self.order.action_confirm()
        self.assertEqual(
            self.order.picking_ids.delivery_zone_id,
            self.partner.delivery_zone_id,
        )

    def test_stock_picking(self):
        partner2 = self.env["res.partner"].create(
            {"name": "partner 2", "delivery_zone_id": self.delivery_zone_b.id}
        )
        self.order.action_confirm()
        self.order.picking_ids.partner_id = partner2
        self.assertEqual(
            self.order.picking_ids.delivery_zone_id, self.delivery_zone_b
        )

    def _get_ctx_from_view(self, res):
        partner_xml = etree.XML(res["arch"])
        partner_path = "//field[@name='child_ids']"
        partner_field = partner_xml.xpath(partner_path)[0]
        return partner_field.attrib.get("context", "{}")

    def test_default_line_discount_value(self):
        res = self.partner.get_view(
            view_id=self.env.ref("partner_delivery_zone.view_partner_form").id,
            view_type="form",
        )
        ctx = self._get_ctx_from_view(res)
        self.assertTrue("default_delivery_zone_id" in ctx)
        view = self.View.create(
            {
                "name": "test",
                "type": "form",
                "model": "res.partner",
                "arch": """
                <form>
                    <field name='child_ids'
                        context="{'default_name': 'test'}">
                    </field>
                </form>
            """,
            }
        )
        res = self.partner.get_view(view_id=view.id, view_type="form")
        ctx = self._get_ctx_from_view(res)
        self.assertTrue("default_delivery_zone_id" in ctx)
