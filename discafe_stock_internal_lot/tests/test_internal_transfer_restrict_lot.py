# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestInternalTransferRestrictLot(TransactionCase):
    """Cobertura de discafe_stock_internal_lot: el campo auxiliar
    allowed_restrict_lot_ids filtra los lotes ofrecidos en 'Restringir Lote'
    reproduciendo el flujo del traslado interno FRG1/INT/00011."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Quant = cls.env["stock.quant"]
        cls.Lot = cls.env["stock.lot"]
        cls.Move = cls.env["stock.move"]

        cls.src_location = cls.env["stock.location"].create({
            "name": "Origen Test",
            "usage": "internal",
            "location_id": cls.env.ref("stock.stock_location_locations").id,
        })
        cls.dest_location = cls.env["stock.location"].create({
            "name": "Destino Test",
            "usage": "internal",
            "location_id": cls.env.ref("stock.stock_location_locations").id,
        })
        cls.internal_type = cls.env.ref("stock.picking_type_internal")

        cls.product = cls.env["product.product"].create({
            "name": "Producto Lote A",
            "type": "consu",
            "is_storable": True,
            "tracking": "lot",
        })
        cls.other_product = cls.env["product.product"].create({
            "name": "Producto Lote B",
            "type": "consu",
            "is_storable": True,
            "tracking": "lot",
        })

        cls.lot_in_stock = cls.Lot.create({
            "name": "LOT-A-STOCK",
            "product_id": cls.product.id,
        })
        cls.lot_no_stock = cls.Lot.create({
            "name": "LOT-A-EMPTY",
            "product_id": cls.product.id,
        })
        cls.lot_other_product = cls.Lot.create({
            "name": "LOT-B",
            "product_id": cls.other_product.id,
        })

        cls.Quant._update_available_quantity(
            cls.product, cls.src_location, 5.0, lot_id=cls.lot_in_stock)
        cls.Quant._update_available_quantity(
            cls.other_product, cls.src_location, 5.0,
            lot_id=cls.lot_other_product)

    def _create_internal_move(self):
        picking = self.env["stock.picking"].create({
            "picking_type_id": self.internal_type.id,
            "location_id": self.src_location.id,
            "location_dest_id": self.dest_location.id,
        })
        return self.Move.create({
            "name": "Traslado Test",
            "product_id": self.product.id,
            "product_uom_qty": 1.0,
            "product_uom": self.product.uom_id.id,
            "location_id": self.src_location.id,
            "location_dest_id": self.dest_location.id,
            "picking_id": picking.id,
        })

    def test_internal_move_offers_only_product_lots_with_stock(self):
        move = self._create_internal_move()
        allowed = move.allowed_restrict_lot_ids
        self.assertIn(self.lot_in_stock, allowed)
        self.assertNotIn(self.lot_no_stock, allowed)
        self.assertNotIn(self.lot_other_product, allowed)

    def test_internal_move_excludes_lot_without_available_stock(self):
        move = self._create_internal_move()
        # Reservar todo el stock del lote deja disponible 0 -> no ofertable.
        self.Quant._update_reserved_quantity(
            self.product, self.src_location, 5.0, lot_id=self.lot_in_stock)
        move.invalidate_recordset(["allowed_restrict_lot_ids"])
        self.assertNotIn(self.lot_in_stock, move.allowed_restrict_lot_ids)

    def test_non_internal_move_filters_only_by_product(self):
        picking = self.env["stock.picking"].create({
            "picking_type_id": self.env.ref("stock.picking_type_out").id,
            "location_id": self.src_location.id,
            "location_dest_id": self.env.ref(
                "stock.stock_location_customers").id,
        })
        move = self.Move.create({
            "name": "Salida Test",
            "product_id": self.product.id,
            "product_uom_qty": 1.0,
            "product_uom": self.product.uom_id.id,
            "location_id": self.src_location.id,
            "location_dest_id": self.env.ref(
                "stock.stock_location_customers").id,
            "picking_id": picking.id,
        })
        allowed = move.allowed_restrict_lot_ids
        self.assertIn(self.lot_in_stock, allowed)
        self.assertIn(self.lot_no_stock, allowed)
        self.assertNotIn(self.lot_other_product, allowed)

    def test_move_without_product_has_no_allowed_lots(self):
        move = self.Move.new({
            "location_id": self.src_location.id,
            "picking_code": "internal",
        })
        self.assertFalse(move.allowed_restrict_lot_ids)
