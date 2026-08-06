# -*- coding: utf-8 -*-

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestSelectUserWarehouse(TransactionCase):
    """Cubre el campo warehouse_id en res.users, el override de
    _get_default_warehouse_id (que hace que el pedido cargue el almacén del
    usuario a través del compute estándar) y la validación de default_get."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.SaleOrder = cls.env["sale.order"]
        cls.company = cls.env.company
        cls.company_warehouse = cls.env["stock.warehouse"].search(
            [("company_id", "=", cls.company.id)], limit=1
        )
        cls.user_warehouse = cls.env["stock.warehouse"].create({
            "name": "Almacén Usuario",
            "code": "WHUSR",
            "company_id": cls.company.id,
        })
        salesman_group = cls.env.ref("sales_team.group_sale_salesman")
        cls.user_with_wh = cls.env["res.users"].create({
            "name": "User With Warehouse",
            "login": "test_user_with_wh",
            "groups_id": [(4, salesman_group.id)],
            "warehouse_id": cls.user_warehouse.id,
        })
        cls.user_without_wh = cls.env["res.users"].create({
            "name": "User Without Warehouse",
            "login": "test_user_without_wh",
            "groups_id": [(4, salesman_group.id)],
        })

    def test_warehouse_field_on_user(self):
        self.assertEqual(self.user_with_wh.warehouse_id, self.user_warehouse)
        self.assertFalse(self.user_without_wh.warehouse_id)

    def test_get_default_warehouse_returns_user_warehouse(self):
        warehouse = self.user_with_wh.with_company(
            self.company
        )._get_default_warehouse_id()
        self.assertEqual(warehouse, self.user_warehouse)

    def test_get_default_warehouse_falls_back_to_super(self):
        warehouse = self.user_without_wh.with_company(
            self.company
        )._get_default_warehouse_id()
        self.assertEqual(warehouse, self.company_warehouse)

    def test_new_order_uses_user_warehouse(self):
        order = self.SaleOrder.with_user(self.user_with_wh).new(
            {"user_id": self.user_with_wh.id}
        )
        self.assertEqual(order.warehouse_id, self.user_warehouse)

    def test_warehouse_follows_current_user_not_salesperson(self):
        other_warehouse = self.env["stock.warehouse"].create({
            "name": "Almacén Otro",
            "code": "WHOTR",
            "company_id": self.company.id,
        })
        salesman_group = self.env.ref("sales_team.group_sale_salesman")
        other_user = self.env["res.users"].create({
            "name": "Other Salesman",
            "login": "test_other_salesman",
            "groups_id": [(4, salesman_group.id)],
            "warehouse_id": other_warehouse.id,
        })
        order = self.SaleOrder.with_user(self.user_with_wh).new(
            {"user_id": other_user.id}
        )
        self.assertEqual(order.warehouse_id, self.user_warehouse)

    def test_default_get_raises_when_user_has_no_warehouse(self):
        with self.assertRaises(UserError):
            self.SaleOrder.with_user(self.user_without_wh).default_get(
                ["warehouse_id"]
            )
