__author__ = "Michael PW"

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Location(models.Model):
    _name = "dalsil.location"
    _inherit = "ss.model"
    _description = "Location"

    name = fields.Char("Nama Lokasi")
    note = fields.Text("Keterangan")
    active = fields.Boolean("Is Active ?", default=True)
    is_customer = fields.Boolean("Is Customer", default=False)
    is_supplier = fields.Boolean("Is Supplier", default=False)