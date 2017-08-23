from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class ResPartner(models.Model):
    """
    Res Partner
    """
    _inherit = "res.partner"

    is_driver = fields.Boolean("Sopir ?", default=False)
