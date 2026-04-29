# -*- coding: utf-8 -*-

{
    'name': 'document_format_dis',
    'summary': """Formatos de documentos DIS""",
    'version': '18.0.1.0.0',
    'description': """Formatos de documentos DIS""",
    'author': 'DDL',
    'company': 'Xtendoo',
    'website': 'http://www.xtendoo.es',
    'category': 'Extra Tools',
    'depends': [
        'base',
        'account',
        'sale',
        'sale_stock',
        'purchase',
        'purchase_stock',
        'web',
        'stock',
        'l10n_es_partner',
        'partner_delivery_zone',
    ],
    'license': 'AGPL-3',
    'data': [

        # Comentario migración Odoo 18: se recuperan también las vistas PDF normales.

        # Ventas PDF
        'views/sale/report_saleorder_document_without_promotions.xml',
        'views/sale/report_saleorder_document_promotions.xml',
        'views/sale/saleorder_promotions.xml',

        # Albaranes PDF
        'views/delivery/report_delivery_document_without_promotions.xml',
        'views/delivery/report_delivery_document_promotions.xml',
        'views/delivery/delivery_promotions.xml',

        # Informe de carga PDF
        'views/workload/stock_picking_report.xml',

        # Facturas PDF
        'views/invoice/report_invoice_document_without_promotions.xml',
        'views/invoice/report_invoice_document_promotions.xml',
        'views/invoice/invoice_promotions.xml',
        'views/invoice_with_description/report_invoice_document_with_description.xml',
        'views/invoice_with_description/invoice_with_description.xml',
        'views/invoice_without_promotions/invoice_without_promotions.xml',

        # Pagos PDF
        'views/payment/report_payment_receipt.xml',

        # Compras PDF
        'views/purchase/report_purchase_document.xml',

        'views/layout/external_layout_clean.xml',

        # Sólo vistas Bluetooth (se han eliminado las vistas "normales")

        # Ventas Bluetooth
        'views/sale_bluetooth/report_saleorder_bluetooth_without_promotions.xml',
        'views/sale_bluetooth/report_saleorder_bluetooth_with_promotions.xml',
        'views/sale_bluetooth/saleorder_promotions_bluetooth.xml',

        # Albarán Bluetooth
        'views/delivery_bluetooth/report_delivery_document_with_promotions_bluetooth.xml',
        'views/delivery_bluetooth/report_delivery_document_without_promotions_bluetooth.xml',
        'views/delivery_bluetooth/delivery_promotions_bluetooth.xml',

        # Factura Bluetooth
        'views/invoice_bluetooth/report_invoice_document_with_promotions_bluetooth.xml',
        'views/invoice_bluetooth/report_invoice_document_without_promotions_bluetooth.xml',
        'views/invoice_bluetooth/invoice_promotions_bluetooth.xml',

        # Pagos Bluetooth
        'views/payment_bluetooth/report_payment_receipt_bluetooth.xml',


    ],
    'demo': [],
    'installable': True,
    'auto_install': False,

}
