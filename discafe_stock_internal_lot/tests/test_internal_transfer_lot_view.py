# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from lxml import etree

from odoo.tests.common import TransactionCase


class TestInternalTransferLotView(TransactionCase):
    at_install = False
    post_install = True

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.detail_view = cls.env.ref("stock.view_stock_move_line_detailed_operation_tree")
        cls.picking_form_view = cls.env.ref("stock.view_picking_form")

    def _get_field_attrs(self, picking_code, show_lots_text=False):
        view = self.env["stock.move.line"].with_context(
            picking_code=picking_code,
            show_lots_text=show_lots_text,
        ).get_view(view_id=self.detail_view.id, view_type="list")
        xml = etree.fromstring(view["arch"])
        lot_id = xml.xpath("//field[@name='lot_id']")[0]
        lot_name = xml.xpath("//field[@name='lot_name']")[0]
        return lot_id.attrib, lot_name.attrib

    def test_internal_transfer_uses_existing_lot_selector(self):
        lot_id_attrs, lot_name_attrs = self._get_field_attrs("internal")
        self.assertEqual(
            lot_id_attrs.get("column_invisible"),
            "context.get('picking_code') not in ('incoming', 'internal') or "
            "context.get('show_lots_text') or "
            "(context.get('picking_code') == 'internal' and not "
            "picking_type_use_existing_lots)",
        )
        self.assertEqual(
            lot_name_attrs.get("column_invisible"),
            "context.get('picking_code') not in ('incoming', 'internal') or "
            "not context.get('show_lots_text')",
        )

    def test_operations_restrict_lot_is_editable(self):
        view = self.env["stock.picking"].get_view(
            view_id=self.picking_form_view.id,
            view_type="form",
        )
        xml = etree.fromstring(view["arch"])
        restrict_lot = xml.xpath(
            "//field[@name='move_ids_without_package']/list/field[@name='restrict_lot_id']"
        )[0]
        self.assertNotIn("readonly", restrict_lot.attrib)
