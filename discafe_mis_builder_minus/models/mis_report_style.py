from odoo import api, models


class MisReportStyle(models.Model):
    _inherit = "mis.report.style"

    @api.model
    def render_num(self, *args, **kwargs):
        result = super().render_num(*args, **kwargs)
        return result.replace("\N{NON-BREAKING HYPHEN}", "-")
