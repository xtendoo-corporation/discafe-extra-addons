# -*- coding: utf-8 -*-
from odoo import models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    def _onchange_group_stock_production_lot(self):
        # No-op: el campo 'group_stock_production_lot' se declara con
        # group='base.group_user,base.group_portal', y res.config.settings
        # calcula su valor por defecto exigiendo que el grupo implicado
        # (stock.group_production_lot) esté en los implied_ids de AMBOS
        # grupos de referencia (ver odoo/addons/base/models/res_config.py,
        # default_get: all(implied_group in group.implied_ids for group
        # in groups)). base.group_portal nunca implica ese grupo interno
        # (no tendria sentido dar permisos de stock a un usuario de
        # portal), asi que este checkbox siempre calcula False al abrir
        # Ajustes, independientemente de si se usa lotes/series o no.
        # El comportamiento por defecto (stock/models/res_config_settings.py)
        # aprovecha ese onchange para desactivar tambien 'Fechas de
        # caducidad' (module_product_expiry), lo que dispara el aviso de
        # desinstalacion nada mas entrar en Ajustes, sin que nadie toque
        # nada. Anulamos el efecto colateral sobre module_product_expiry
        # para que 'Fechas de caducidad' no dependa de un calculo que
        # estructuralmente nunca puede dar True en esta instalacion.
        pass
