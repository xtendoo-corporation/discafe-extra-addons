# -*- coding: utf-8 -*-

{
    'name': 'Product show tax in tree view',
    'summary': """Mostrar impuestos en la vista de lista de productos""",
    'version': '18.0.1.0.0',
    'description': """Mostrar impuestos en la vista de lista de productos""",
    'author': 'DDL',
    'company': 'Xtendoo',
    'website': 'http://www.xtendoo.com',
    'category': 'Extra Tools',
    'depends': [
        'base',
        'product',
        'account',
    ],
    'license': 'AGPL-3',
    'data': [
        'views/product_template_show_tax.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,

}
