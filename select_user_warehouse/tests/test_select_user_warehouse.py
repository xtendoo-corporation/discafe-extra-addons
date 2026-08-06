# -*- coding: utf-8 -*-

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestSelectUserWarehouse(TransactionCase):
    """Cubre el campo warehouse_id en res.users y las dos ramas de
    sale.order.default_get (usuario con almacén y usuario sin almacén)."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.SaleOrder = cls.env["sale.order"]
        cls.warehouse = cls.env["stock.warehouse"].search([], limit=1)
        salesman_group = cls.env.ref("sales_team.group_sale_salesman")
        cls.user_with_wh = cls.env["res.users"].create({
            "name": "User With Warehouse",
            "login": "test_user_with_wh",
            "groups_id": [(4, salesman_group.id)],
            "warehouse_id": cls.warehouse.id,
        })
        cls.user_without_wh = cls.env["res.users"].create({
            "name": "User Without Warehouse",
            "login": "test_user_without_wh",
            "groups_id": [(4, salesman_group.id)],
        })

    def test_warehouse_field_on_user(self):
        self.assertEqual(self.user_with_wh.warehouse_id, self.warehouse)
        self.assertFalse(self.user_without_wh.warehouse_id)

    def test_default_get_sets_warehouse_when_user_has_one(self):
        defaults = self.SaleOrder.with_user(self.user_with_wh).default_get(
            ["warehouse_id"]
        )
        self.assertEqual(defaults.get("warehouse_id"), self.warehouse.id)

    def test_default_get_raises_when_user_has_no_warehouse(self):
        with self.assertRaises(UserError):
            self.SaleOrder.with_user(self.user_without_wh).default_get(
                ["warehouse_id"]
            )
