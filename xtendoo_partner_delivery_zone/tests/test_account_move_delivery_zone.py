# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from unittest.mock import MagicMock, patch

from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestAccountMoveDeliveryZone(TransactionCase):
    """La factura debe tomar la zona de entrega que el usuario tiene
    seleccionada en la sesión (ruta), no la del cliente, cuando hay ruta
    activa. Sin ruta activa mantiene la zona del cliente."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Move = cls.env["account.move"]

        cls.zone = cls.env["partner.delivery.zone"].create({
            "name": "Zona Factura",
            "code": "ZF",
        })
        cls.other_zone = cls.env["partner.delivery.zone"].create({
            "name": "Otra Zona Factura",
            "code": "OZF",
        })
        cls.partner_other_zone = cls.env["res.partner"].create({
            "name": "Cliente factura otra zona",
            "delivery_zone_id": cls.other_zone.id,
        })
        cls.partner_no_zone = cls.env["res.partner"].create({
            "name": "Cliente factura sin zona",
        })

        cls.account_manager = cls.env["res.users"].create({
            "name": "Gestor Contable Factura",
            "login": "account_manager_invoice_zone@example.com",
            "groups_id": [
                (4, cls.env.ref("base.group_user").id),
                (4, cls.env.ref("account.group_account_manager").id),
            ],
        })
        cls.regular_user = cls.env["res.users"].create({
            "name": "Usuario Regular Factura",
            "login": "regular_invoice_zone@example.com",
            "groups_id": [
                (4, cls.env.ref("base.group_user").id),
                (4, cls.env.ref("account.group_account_invoice").id),
            ],
        })

    def _mock_request(self, zone_id):
        request = MagicMock()
        request.session = {"partner_delivery_zone_id": zone_id}
        return patch("odoo.http.request", request)

    def _new_invoice(self, partner):
        return self.Move.new({
            "move_type": "out_invoice",
            "partner_id": partner.id,
        })

    def test_invoice_uses_session_zone_over_partner_zone(self):
        with self._mock_request(self.zone.id):
            move = self._new_invoice(self.partner_other_zone)
            self.assertEqual(move.delivery_zone_id, self.zone)

    def test_invoice_uses_session_zone_for_partner_without_zone(self):
        with self._mock_request(self.zone.id):
            move = self._new_invoice(self.partner_no_zone)
            self.assertEqual(move.delivery_zone_id, self.zone)

    def test_invoice_falls_back_to_partner_zone_without_session(self):
        with patch("odoo.http.request", None):
            move = self._new_invoice(self.partner_other_zone)
            self.assertEqual(move.delivery_zone_id, self.other_zone)

    def test_invoice_ignores_stale_session_zone(self):
        with self._mock_request(999999):
            move = self._new_invoice(self.partner_other_zone)
            self.assertEqual(move.delivery_zone_id, self.other_zone)

    def test_account_manager_can_edit_delivery_zone(self):
        """can_edit_delivery_zone is True for account.group_account_manager."""
        move = self.Move.with_user(self.account_manager).new({
            "move_type": "out_invoice",
            "partner_id": self.partner_other_zone.id,
        })
        self.assertTrue(move.can_edit_delivery_zone)

    def test_regular_user_cannot_edit_delivery_zone(self):
        """can_edit_delivery_zone is False without account.group_account_manager."""
        move = self.Move.with_user(self.regular_user).new({
            "move_type": "out_invoice",
            "partner_id": self.partner_other_zone.id,
        })
        self.assertFalse(move.can_edit_delivery_zone)
