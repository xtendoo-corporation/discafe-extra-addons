# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import date
from unittest.mock import MagicMock, PropertyMock, patch

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestSaleOrderDeliveryZone(TransactionCase):
    """Cobertura completa de xtendoo_partner_delivery_zone/models/sale_order.py:
    _get_delivery_zone_id, _get_next_partner, default_get, la restricción
    _check_delivery_zone_id, create y button_next_partner."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.SaleOrder = cls.env["sale.order"]
        cls.Visit = cls.env["partner.delivery.zone.visit"]
        cls.Line = cls.env["delivery.zone.partner.line"]

        # select_user_warehouse.default_get exige almacén en el usuario actual.
        cls.warehouse = cls.env["stock.warehouse"].search([], limit=1)
        cls.env.user.warehouse_id = cls.warehouse

        cls.zone = cls.env["partner.delivery.zone"].create({
            "name": "Zona Test",
            "code": "ZT",
        })
        cls.other_zone = cls.env["partner.delivery.zone"].create({
            "name": "Otra Zona",
            "code": "OZ",
        })
        cls.partner_a = cls.env["res.partner"].create({
            "name": "Cliente A",
            "delivery_zone_id": cls.zone.id,
        })
        cls.partner_b = cls.env["res.partner"].create({
            "name": "Cliente B",
            "delivery_zone_id": cls.zone.id,
        })
        cls.partner_other_zone = cls.env["res.partner"].create({
            "name": "Cliente otra zona",
            "delivery_zone_id": cls.other_zone.id,
        })
        cls.partner_no_zone = cls.env["res.partner"].create({
            "name": "Cliente sin zona",
        })
        cls.product = cls.env["product.product"].create({
            "name": "Producto Test",
            "type": "service",
        })
        cls.Line.create({
            "delivery_zone_id": cls.zone.id,
            "partner_id": cls.partner_a.id,
            "sequence": 1,
        })
        cls.Line.create({
            "delivery_zone_id": cls.zone.id,
            "partner_id": cls.partner_b.id,
            "sequence": 2,
        })

    def _mock_request(self, zone_id):
        request = MagicMock()
        request.session = {"partner_delivery_zone_id": zone_id}
        return patch("odoo.http.request", request)

    def _visit_exists(self, zone, partner):
        return bool(self.Visit.search([
            ("delivery_zone_id", "=", zone.id),
            ("partner_id", "=", partner.id),
            ("date", "=", date.today()),
        ]))

    # -- _get_delivery_zone_id -------------------------------------------------
    def test_get_delivery_zone_id_without_request(self):
        with patch("odoo.http.request", None):
            self.assertFalse(self.SaleOrder._get_delivery_zone_id())

    def test_get_delivery_zone_id_from_session(self):
        with self._mock_request(self.zone.id):
            self.assertEqual(
                self.SaleOrder._get_delivery_zone_id(), self.zone.id)

    def test_get_delivery_zone_id_handles_exception(self):
        request = MagicMock()
        type(request).session = PropertyMock(side_effect=Exception("boom"))
        with patch("odoo.http.request", request):
            self.assertFalse(self.SaleOrder._get_delivery_zone_id())

    # -- default_get -----------------------------------------------------------
    def test_default_get_without_session(self):
        res = self.SaleOrder.default_get(["partner_id", "delivery_zone_id"])
        self.assertNotIn("delivery_zone_id", res)
        self.assertFalse(res.get("partner_id"))

    def test_default_get_with_session_sets_partner_and_zone(self):
        with self._mock_request(self.zone.id):
            res = self.SaleOrder.default_get(
                ["partner_id", "delivery_zone_id"])
        self.assertEqual(res.get("delivery_zone_id"), self.zone.id)
        self.assertEqual(res.get("partner_id"), self.partner_a.id)

    # -- _compute_delivery_zone_id --------------------------------------------
    def test_compute_uses_session_zone_over_partner_zone(self):
        with self._mock_request(self.zone.id):
            order = self.SaleOrder.new({"partner_id": self.partner_other_zone.id})
            self.assertEqual(order.delivery_zone_id, self.zone)

    def test_compute_uses_session_zone_for_partner_without_zone(self):
        with self._mock_request(self.zone.id):
            order = self.SaleOrder.new({"partner_id": self.partner_no_zone.id})
            self.assertEqual(order.delivery_zone_id, self.zone)

    def test_compute_falls_back_to_partner_zone_without_session(self):
        with patch("odoo.http.request", None):
            order = self.SaleOrder.new({"partner_id": self.partner_other_zone.id})
            self.assertEqual(order.delivery_zone_id, self.other_zone)

    def test_compute_ignores_stale_session_zone(self):
        with self._mock_request(999999):
            order = self.SaleOrder.new({"partner_id": self.partner_other_zone.id})
            self.assertEqual(order.delivery_zone_id, self.other_zone)

    # -- _check_delivery_zone_id (constrains) ----------------------------------
    def test_create_with_zone_ok_and_visit_created(self):
        order = self.SaleOrder.create({
            "partner_id": self.partner_a.id,
            "delivery_zone_id": self.zone.id,
        })
        self.assertEqual(order.delivery_zone_id, self.zone)
        self.assertTrue(self._visit_exists(self.zone, self.partner_a))

    def test_create_without_zone_raises(self):
        with self.assertRaises(ValidationError):
            self.SaleOrder.create({"partner_id": self.partner_no_zone.id})

    def test_write_clearing_zone_raises(self):
        order = self.SaleOrder.create({
            "partner_id": self.partner_a.id,
            "delivery_zone_id": self.zone.id,
        })
        with self.assertRaises(ValidationError):
            order.write({"delivery_zone_id": False})
            order.flush_recordset()

    # -- create (resolución desde sesión) --------------------------------------
    def test_create_resolves_zone_from_session(self):
        with self._mock_request(self.zone.id):
            order = self.SaleOrder.create({"partner_id": self.partner_a.id})
        self.assertEqual(order.delivery_zone_id, self.zone)
        self.assertTrue(self._visit_exists(self.zone, self.partner_a))

    # -- button_next_partner ---------------------------------------------------
    def test_button_next_partner_readonly_raises(self):
        order = self.SaleOrder.create({
            "partner_id": self.partner_a.id,
            "delivery_zone_id": self.zone.id,
            "order_line": [(0, 0, {
                "product_id": self.product.id,
                "product_uom_qty": 1.0,
            })],
        })
        self.assertTrue(order.partner_id_readonly)
        with self.assertRaises(ValidationError):
            order.button_next_partner()

    def test_button_next_partner_without_zone_returns(self):
        order = self.SaleOrder.new({})
        self.assertFalse(order.partner_id_readonly)
        self.assertIsNone(order.button_next_partner())

    def test_button_next_partner_sets_next_partner(self):
        order = self.SaleOrder.create({
            "partner_id": self.partner_a.id,
            "delivery_zone_id": self.zone.id,
        })
        with self._mock_request(self.zone.id):
            order.button_next_partner()
        self.assertTrue(self._visit_exists(self.zone, self.partner_a))
        self.assertEqual(order.partner_id, self.partner_b)

    def test_button_next_partner_no_more_partners_raises(self):
        order = self.SaleOrder.create({
            "partner_id": self.partner_a.id,
            "delivery_zone_id": self.zone.id,
        })
        self.Visit.create_if_not_exist(self.zone.id, self.partner_a.id)
        self.Visit.create_if_not_exist(self.zone.id, self.partner_b.id)
        with self._mock_request(self.zone.id):
            with self.assertRaises(ValidationError):
                order.button_next_partner()
