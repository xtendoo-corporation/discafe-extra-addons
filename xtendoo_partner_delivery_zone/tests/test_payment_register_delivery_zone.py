# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
"""Tests for account.payment.register delivery_zone_id extension.

Coverage:
  - Default priority: session zone > source document zone > partner zone.
  - Stale session zone (non-existent DB ID) → correct fallback.
  - Admin manual selection propagates to the created account.payment.
  - Default zone propagates to the created account.payment.
  - can_edit_delivery_zone: False for regular users, True for admin group.
  - Server-side enforcement: _effective_delivery_zone ignores a non-admin's
    direct write and always re-derives the default.
  - Existing account.payment session/partner zone compute is not broken.

Design notes
------------
* Default-priority and session-zone tests use `.new()` so the compute runs
  synchronously *while* the HTTP-session mock is active; field access must
  also happen inside the mock context for lazy computes on `.new()` records.
* Propagation tests call `action_create_payments()` as *admin_user* because
  d_hr_administration.account_payment overrides `action_cancel` with a hard
  group-check that fires even on empty recordsets.
* User-context switching uses `model.with_user(user)` (BaseModel API), not
  `env.with_user()` which does not exist in Odoo 18.
"""
from unittest.mock import MagicMock, patch

from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestPaymentRegisterDeliveryZone(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.zone = cls.env["partner.delivery.zone"].create({
            "name": "Zona Register Test",
            "code": "ZRT",
        })
        cls.other_zone = cls.env["partner.delivery.zone"].create({
            "name": "Otra Zona Register",
            "code": "OZRT",
        })

        cls.partner = cls.env["res.partner"].create({
            "name": "Cliente Register Zone",
            "delivery_zone_id": cls.zone.id,
        })
        cls.partner_other_zone = cls.env["res.partner"].create({
            "name": "Cliente Otra Zona Register",
            "delivery_zone_id": cls.other_zone.id,
        })
        cls.partner_no_zone = cls.env["res.partner"].create({
            "name": "Cliente Sin Zona Register",
        })

        cls.bank_journal = cls.env["account.journal"].search(
            [("type", "=", "bank"), ("company_id", "=", cls.env.company.id)],
            limit=1,
        )

        cls.product = cls.env["product.product"].create({
            "name": "Producto Test Register",
            "type": "service",
            "taxes_id": [],
        })

        # Posted invoices used across tests.
        cls.invoice = cls._make_posted_invoice(cls.partner, 100.0)            # zone = cls.zone
        cls.invoice_other_zone = cls._make_posted_invoice(cls.partner_other_zone, 50.0)  # zone = cls.other_zone
        cls.invoice_no_doc_zone = cls._make_posted_invoice(cls.partner_no_zone, 30.0)   # zone = False

        # User WITH d_hr_administration.administration + accounting rights.
        # Required for propagation tests because d_hr_administration overrides
        # action_cancel with a permission check that fires even on empty
        # recordsets.
        cls.admin_user = cls.env["res.users"].create({
            "name": "Admin Register Zone Tests",
            "login": "admin_register_zone_tests@example.com",
            "groups_id": [
                (4, cls.env.ref("base.group_user").id),
                (4, cls.env.ref("account.group_account_invoice").id),
                (4, cls.env.ref("account.group_account_user").id),
                (4, cls.env.ref("d_hr_administration.administration").id),
            ],
        })

        # User WITHOUT the administration group (for permission tests).
        cls.regular_user = cls.env["res.users"].create({
            "name": "Regular Register Zone Tests",
            "login": "regular_register_zone_tests@example.com",
            "groups_id": [
                (4, cls.env.ref("base.group_user").id),
                (4, cls.env.ref("account.group_account_invoice").id),
            ],
        })

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @classmethod
    def _make_posted_invoice(cls, partner, price_unit):
        """Create and post a customer invoice for *partner*."""
        invoice = cls.env["account.move"].create({
            "move_type": "out_invoice",
            "partner_id": partner.id,
            "invoice_line_ids": [(0, 0, {
                "product_id": cls.product.id,
                "price_unit": price_unit,
                "quantity": 1,
            })],
        })
        invoice.action_post()
        return invoice

    def _wizard_model(self, user=None):
        """Return the account.payment.register model, optionally as *user*.

        Uses model.with_user() (BaseModel API) not env.with_user() which does
        not exist in Odoo 18.
        """
        model = self.env["account.payment.register"]
        return model.with_user(user) if user else model

    def _new_wizard(self, invoice, user=None):
        """Return an in-memory wizard (.new()) for *invoice*.

        .new() records are lazy-computed: the compute runs on first field
        access, making them ideal for session-mock tests (access the field
        *while* the mock is still active).
        """
        return (
            self._wizard_model(user)
            .with_context(active_model="account.move", active_ids=[invoice.id])
            .new({})
        )

    def _create_wizard(self, invoice, user=None):
        """Create and save a wizard record for *invoice* (no session mock).

        With precompute=True on delivery_zone_id the compute is called at
        INSERT time, so the stored value is correct even without mocking.
        """
        return (
            self._wizard_model(user)
            .with_context(active_model="account.move", active_ids=[invoice.id])
            .create({})
        )

    def _mock_session(self, zone_id):
        req = MagicMock()
        req.session = {"partner_delivery_zone_id": zone_id}
        return patch("odoo.http.request", req)

    # ------------------------------------------------------------------
    # Default priority  (use .new() + access field inside mock context)
    # ------------------------------------------------------------------

    def test_default_session_zone_has_priority(self):
        """Active session zone wins over document zone and partner zone."""
        with self._mock_session(self.other_zone.id):
            wizard = self._new_wizard(self.invoice)
            zone = wizard.delivery_zone_id  # access inside mock → lazy compute
        self.assertEqual(zone, self.other_zone)

    def test_default_source_document_zone_without_session(self):
        """Without a session, the wizard defaults to the source invoice zone."""
        with patch("odoo.http.request", None):
            wizard = self._new_wizard(self.invoice_other_zone)
            zone = wizard.delivery_zone_id
        self.assertEqual(zone, self.other_zone)

    def test_default_partner_zone_when_no_session_no_document_zone(self):
        """No session, no doc zone → falls back to partner zone."""
        partner_with_zone = self.env["res.partner"].create({
            "name": "Con Zona Fallback",
            "delivery_zone_id": self.zone.id,
        })
        invoice = self._make_posted_invoice(partner_with_zone, 10.0)
        invoice.write({"delivery_zone_id": False})
        invoice.flush_recordset()

        with patch("odoo.http.request", None):
            wizard = self._new_wizard(invoice)
            zone = wizard.delivery_zone_id
        self.assertEqual(zone, self.zone)

    def test_default_empty_when_no_source_at_all(self):
        """No session, no doc zone, no partner zone → field is empty."""
        with patch("odoo.http.request", None):
            wizard = self._new_wizard(self.invoice_no_doc_zone)
            zone = wizard.delivery_zone_id
        self.assertFalse(zone)

    # ------------------------------------------------------------------
    # Stale session zone
    # ------------------------------------------------------------------

    def test_stale_session_zone_falls_back_to_source_document_zone(self):
        """Session zone ID that does not exist in DB is silently ignored."""
        with self._mock_session(999999):
            wizard = self._new_wizard(self.invoice)
            zone = wizard.delivery_zone_id
        self.assertEqual(zone, self.zone)

    def test_stale_session_zone_falls_back_to_partner_zone(self):
        """Stale session + no doc zone → partner zone."""
        partner_with_zone = self.env["res.partner"].create({
            "name": "Con Zona Stale",
            "delivery_zone_id": self.other_zone.id,
        })
        invoice = self._make_posted_invoice(partner_with_zone, 20.0)
        invoice.write({"delivery_zone_id": False})
        invoice.flush_recordset()

        with self._mock_session(999999):
            wizard = self._new_wizard(invoice)
            zone = wizard.delivery_zone_id
        self.assertEqual(zone, self.other_zone)

    # ------------------------------------------------------------------
    # Propagation to account.payment
    # (admin_user used so d_hr_administration.action_cancel does not fire)
    # ------------------------------------------------------------------

    def test_default_zone_propagates_to_created_payment(self):
        """The default zone (from source doc) is stamped on the created payment."""
        with patch("odoo.http.request", None):
            wizard = self._create_wizard(self.invoice_other_zone, user=self.admin_user)
        self.assertEqual(wizard.delivery_zone_id, self.other_zone)

        wizard.journal_id = self.bank_journal
        wizard.action_create_payments()

        payment = self.env["account.payment"].search(
            [
                ("partner_id", "=", self.partner_other_zone.id),
                ("payment_type", "=", "inbound"),
            ],
            order="id desc",
            limit=1,
        )
        self.assertTrue(payment, "No payment found after action_create_payments")
        self.assertEqual(payment.delivery_zone_id, self.other_zone)

    def test_admin_manual_override_propagates_to_payment(self):
        """Admin's manual zone override is stamped on the created payment."""
        with patch("odoo.http.request", None):
            wizard = self._create_wizard(self.invoice, user=self.admin_user)

        wizard.delivery_zone_id = self.other_zone  # admin override
        wizard.journal_id = self.bank_journal
        wizard.action_create_payments()

        payment = self.env["account.payment"].search(
            [
                ("partner_id", "=", self.partner.id),
                ("payment_type", "=", "inbound"),
            ],
            order="id desc",
            limit=1,
        )
        self.assertTrue(payment)
        self.assertEqual(payment.delivery_zone_id, self.other_zone)

    # ------------------------------------------------------------------
    # Permissions (can_edit_delivery_zone)
    # ------------------------------------------------------------------

    def test_regular_user_cannot_edit_delivery_zone(self):
        """can_edit_delivery_zone is False without d_hr_administration group."""
        with patch("odoo.http.request", None):
            wizard = self._new_wizard(self.invoice, user=self.regular_user)
            can_edit = wizard.can_edit_delivery_zone
        self.assertFalse(can_edit)

    def test_administration_group_user_can_edit_delivery_zone(self):
        """can_edit_delivery_zone is True for d_hr_administration.administration."""
        with patch("odoo.http.request", None):
            wizard = self._new_wizard(self.invoice, user=self.admin_user)
            can_edit = wizard.can_edit_delivery_zone
        self.assertTrue(can_edit)

    # ------------------------------------------------------------------
    # Server-side enforcement via _effective_delivery_zone
    # ------------------------------------------------------------------

    def test_effective_delivery_zone_returns_manual_for_admin(self):
        """Admin's manually set zone is returned by _effective_delivery_zone."""
        with patch("odoo.http.request", None):
            wizard = self._new_wizard(self.invoice, user=self.admin_user)
            wizard.delivery_zone_id = self.other_zone
            effective = wizard._effective_delivery_zone()
        self.assertEqual(effective, self.other_zone)

    def test_effective_delivery_zone_ignores_write_for_non_admin(self):
        """Non-admin direct write to delivery_zone_id is ignored.

        _effective_delivery_zone always re-derives the default for users
        outside the administration group, preventing UI-readonly bypass.
        """
        with patch("odoo.http.request", None):
            wizard = self._new_wizard(self.invoice, user=self.regular_user)
            # Simulate direct-RPC write bypassing the UI readonly.
            wizard.delivery_zone_id = self.other_zone  # tamper
            effective = wizard._effective_delivery_zone()
        # Must be cls.zone (source doc zone), NOT the tampered other_zone.
        self.assertEqual(effective, self.zone)

    # ------------------------------------------------------------------
    # Existing account.payment behaviour — not broken
    # ------------------------------------------------------------------

    def test_existing_payment_session_zone_compute(self):
        """account.payment still reads session zone correctly (existing behaviour)."""
        with self._mock_session(self.other_zone.id):
            payment = self.env["account.payment"].new({
                "payment_type": "inbound",
                "partner_type": "customer",
                "partner_id": self.partner.id,
                "amount": 10.0,
            })
            zone = payment.delivery_zone_id  # access inside mock (lazy compute)
        self.assertEqual(zone, self.other_zone)

    def test_existing_payment_partner_zone_fallback(self):
        """account.payment falls back to partner zone when no session."""
        with patch("odoo.http.request", None):
            payment = self.env["account.payment"].new({
                "payment_type": "inbound",
                "partner_type": "customer",
                "partner_id": self.partner.id,
                "amount": 10.0,
            })
            zone = payment.delivery_zone_id
        self.assertEqual(zone, self.zone)
