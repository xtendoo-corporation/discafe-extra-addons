# __manifest__.py
{
    'name': 'Módulo Básico de Ejemplo',
    'version': '16.0.1.0.0',
    'category': 'Tools',
    'description': 'Un módulo básico para probar el post_init_hook.',
    'author': 'Tu nombre',
    'website': 'http://www.tuempresa.com',
    'depends': [],
    'data': [],
    'post_init_hook': '_post_init_hook',  # Hook de instalación
    'installable': True,
    'application': True,
}
