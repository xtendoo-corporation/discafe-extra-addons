# -*- coding: utf-8 -*-
{
    'name': 'Loyalty Program Amortization',
    'version': '18.0.1.0.0',
    'category': 'Sales/Loyalty',
    'summary': 'Agrega campo de amortización a programas de fidelidad Buy X Get Y',
    'description': """
        Este módulo extiende los programas de fidelidad de Odoo 18 para agregar
        un campo booleano "Amortización" que solo es visible cuando el tipo de
        promoción es "Comprar X recibir Y" (buy_x_get_y).
    """,
    'author': 'Guillermo Bárcena López',
    'depends': [
        'base',
        'sale',
        'loyalty',
        'sale_loyalty',
    ],
    'data': [
        'views/loyalty_program_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
