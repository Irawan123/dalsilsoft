__author__ = "Michael PW"

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Uom(models.Model):
    _name = "dalsil.uom"
    _inherit = "ss.model"
    _description = "Uom"

    name = fields.Char("Nama Satuan Barang", required=True)
    active = fields.Boolean("Is Active ?", default=True)