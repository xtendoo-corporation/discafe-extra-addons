# models/res_partner.py
from odoo import api, models

class ResPartnerInherit(models.Model):
    _inherit = "res.partner"

    @api.model
    def name_search(self, name="", args=None, operator="ilike", limit=100):
        """Protege el campo 'customer' en la búsqueda."""
        if args and any(
            isinstance(arg, (list, tuple)) and arg[0] == "customer" for arg in args
        ):
            if "customer" in self._fields:
                print("args contiene el campo 'customer'")
            else:
                print("El campo 'customer' no existe en esta versión")
                args = [arg for arg in args if not (isinstance(arg, (list, tuple)) and arg[0] == "customer")]
        return super().name_search(name=name, args=args, operator=operator, limit=limit)
