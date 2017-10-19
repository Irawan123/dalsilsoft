from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

MONTH = (
    ("1", _("January")),
    ("2", _("February")),
    ("3", _("March")),
    ("4", _("April")),
    ("5", _("May")),
    ("6", _("June")),
    ("7", _("July")),
    ("8", _("August")),
    ("9", _("September")),
    ("10", _("October")),
    ("11", _("November")),
    ("12", _("December"))
)

class StartStock(models.Model):
    """
    Start Stock
    """
    _name = "dalsil.start_stock"
    _inherit = "ss.model"

    month = fields.Selection(MONTH, "Bulan")
    year = fields.Char("Year", size=4)
    line_ids = fields.One2many("dalsil.start_stock.line", "parent_id", string="Stock")
    note = fields.Text("Internal Note")

    @api.model
    def cron_last_stock(self):
        current_month = str(int(fields.Date.from_string(fields.Date.today()).month))
        current_year = str(int(fields.Date.from_string(fields.Date.today()).year))
        start_stock = self.env["dalsil.start_stock"].sudo().search([
            ("month", "=", current_month),
            ("year", "=", current_year)
        ], limit=1)
        if start_stock:
            for line in start_stock.line_ids:
                line.unlink()
        else:
            start_stock = self.env['dalsil.start_stock'].create({
                'month': current_month,
                'year': current_year
            })

        location_ids = self.env["stock.location"].sudo().search([
            ("usage", "=", 'internal'),
            ("active", "=", True)
        ])
        for location_id in location_ids:
            quant_ids = self.env["stock.quant"].sudo().search([
                ("location_id", "=", location_id.id)
            ])
            dict_quant = {}
            for quant_id in quant_ids:
                key = quant_id.product_id.id
                if key in dict_quant:
                    dict_quant[key]['qty'] += quant_id.qty
                    dict_quant[key]['cost'] += quant_id.cost
                else:
                    dict_quant[key] = {
                        'qty': quant_id.qty,
                        'cost': quant_id.cost
                    }
            for key, quant in dict_quant.iteritems():
                self.env['dalsil.start_stock.line'].create({
                    'parent_id': start_stock.id,
                    'product_id': key,
                    'stock': quant['qty'],
                    'location_id': location_id.id,
                    'inventory_value': quant['cost']
                })