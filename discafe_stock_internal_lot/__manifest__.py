{
    "name": "Discafe Stock Internal Lot",
    "summary": "Restore internal transfer lot editing",
    "version": "18.0.1.0.0",
    "description": "Makes internal transfer lot restriction editable again on operations.",
    "author": "DDL",
    "company": "Xtendoo",
    "website": "http://www.xtendoo.es",
    "category": "Warehouse",
    "depends": ["stock", "stock_restrict_lot"],
    "license": "AGPL-3",
    "data": [
        "views/stock_picking_views.xml",
        "views/stock_move_line_views.xml",
    ],
    "installable": True,
    "auto_install": False,
}
