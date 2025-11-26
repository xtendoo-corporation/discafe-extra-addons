# See LICENSE file for full copyright and licensing details.

{
    'name': 'Xtendoo Web Digital Signature',
    'version': '18.0.1.0.0',
    'author': 'Xtendoo',
    'maintainer': 'Dani Domínguez',
    "license": "AGPL-3",
    'category': 'Tools',
    'description': '''
     This module provides the functionality to store digital signature
     Example can be seen into the User's form view where we have
        added a test field under signature.
    ''',
    'summary': '''
        Touch screen enable so user can add signature with touch devices.
        Digital signature can be very usefull for documents.
    ''',
    'images': ['static/description/Digital_Signature.jpg'],
    'depends': [
        'web',
        'sale',
        'account',
        'stock',
    ],
    'data': [
        'views/users_view.xml',
        'views/sale_view.xml',
        'views/stock_picking_view.xml',
        'views/account_invoice_view.xml',
    ],
    'assets': {
        'web.assets_backend': [
        'web/static/lib/jquery/jquery.js',
        'web_digital_sign/static/lib/jSignature/jSignatureCustom.js',
        'web_digital_sign/static/src/js/digital_sign.js',
        'web_digital_sign/static/src/xml/digital_sign.xml',

        ],
    },
    'website': 'http://www.serpentcs.com',
    'installable': True,
    'auto_install': False,
}
