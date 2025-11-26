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
        'web',
        'stock'
    ],
    'license': 'AGPL-3',
    'data': [

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
