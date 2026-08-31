# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountPaymentRegister(models.TransientModel):
    """Extend the payment-register wizard with a delivery zone field.

    Default priority (highest to lowest):
      1. Active session zone (validated against DB to discard stale IDs).
      2. Zone from the source document (invoice / move line).
      3. Zone of the partner.

    All users can see the field (read).  Only members of the
    *account.group_account_manager* group may change it; that restriction
    is enforced in the UI via *can_edit_delivery_zone* and re-enforced
    server-side in *_effective_delivery_zone* so that direct-RPC writes cannot
    bypass it.
    """

    _inherit = "account.payment.register"

    delivery_zone_id = fields.Many2one(
        comodel_name="partner.delivery.zone",
        string="Delivery Zone",
        ondelete="restrict",
        compute="_compute_delivery_zone_id",
        store=True,
        readonly=False,
    )
    can_edit_delivery_zone = fields.Boolean(
        compute="_compute_can_edit_delivery_zone",
        store=False,
    )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _read_session_zone_id(self):
        """Return the delivery zone ID stored in the HTTP session, or False.

        Designed to be safe outside HTTP contexts (cron, tests, shell):
        *odoo.http.request* is None in those environments and the method
        returns False cleanly without raising.
        """
        from odoo.http import request as http_request  # noqa: PLC0415

        if not http_request or not http_request.session:
            return False
        return http_request.session.get("partner_delivery_zone_id", False)

    def _effective_delivery_zone(self):
        """Return the zone to stamp on the created account.payment.

        Administrators may keep any manual override entered in the form.
        For all other users the zone is re-derived from the priority chain
        (session → source document → partner) so that a direct-RPC write
        on the wizard field cannot bypass the UI readonly restriction.
        """
        self.ensure_one()
        if self.env.user.has_group("account.group_account_manager"):
            return self.delivery_zone_id

        # Non-admin: re-resolve, ignoring any wizard field value.
        Zone = self.env["partner.delivery.zone"]
        session_zone_id = self._read_session_zone_id()
        if session_zone_id:
            zone = Zone.browse(session_zone_id)
            if zone.exists():
                return zone
        source_zone = self.line_ids.move_id.mapped("delivery_zone_id")[:1]
        return source_zone or self.partner_id.delivery_zone_id

    # ------------------------------------------------------------------
    # Compute
    # ------------------------------------------------------------------

    @api.depends_context("uid")
    def _compute_can_edit_delivery_zone(self):
        can_edit = self.env.user.has_group("account.group_account_manager")
        for wizard in self:
            wizard.can_edit_delivery_zone = can_edit

    @api.depends("line_ids", "partner_id")
    def _compute_delivery_zone_id(self):
        """Set delivery_zone_id using the three-level priority chain.

        The session zone is validated once (outside the loop) to avoid
        one DB query per wizard record.
        """
        Zone = self.env["partner.delivery.zone"]

        session_zone_id = self._read_session_zone_id()
        session_zone = Zone
        if session_zone_id:
            candidate = Zone.browse(session_zone_id)
            if candidate.exists():
                session_zone = candidate

        for wizard in self:
            if session_zone:
                wizard.delivery_zone_id = session_zone
            else:
                source_zone = wizard.line_ids.move_id.mapped("delivery_zone_id")[:1]
                wizard.delivery_zone_id = (
                    source_zone or wizard.partner_id.delivery_zone_id
                )

    # ------------------------------------------------------------------
    # Payment value builders — propagate zone to created account.payment
    # ------------------------------------------------------------------

    def _create_payment_vals_from_wizard(self, batch_result):
        vals = super()._create_payment_vals_from_wizard(batch_result)
        zone = self._effective_delivery_zone()
        if zone:
            vals["delivery_zone_id"] = zone.id
        return vals

    def _create_payment_vals_from_batch(self, batch_result):
        vals = super()._create_payment_vals_from_batch(batch_result)
        zone = self._effective_delivery_zone()
        if zone:
            vals["delivery_zone_id"] = zone.id
        return vals
