__author__ = "Michael PW"

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Truck(models.Model):
    _name = "dalsil.truck"
    _inherit = "ss.model"
    _description = "Truck"

    name = fields.Char("Nopol Truk", required=True)
    type_truck = fields.Char("Tipe Truck")
    note = fields.Text("Keterangan")
    active = fields.Boolean("Is Active ?", default=True)