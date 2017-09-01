from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

STATE = (
    ("draft", _("Draft")),
    ("open", _("Open")),
    ("done", _("Done")),
    ("cancel", _("Cancelled")),
)
DEST_TYPE = (
    ("rent", _("Rent")),
    ("warehouse", _("Warehouse")),
    ("customer", _("Customer"))
)


class RentTruck(models.Model):
    """
    Rent Truck
    """
    _name = "dalsil.rent_truck"
    _inherit = "ss.model"
    _state_start = STATE[0][0]

    name = fields.Char("Rent Truck No.")
    state = fields.Selection(STATE, "State")
    truck_id = fields.Many2one("dalsil.truck", "Truck", domain=[("active", "=", True)], required=True)
    driver_id = fields.Many2one("res.partner", "Driver", domain=[("active", "=", True), ("is_driver", "=", True)], required=True)
    customer_rent_id = fields.Many2one("res.partner", "Penyewa Truck", domain=[("active", "=", True), ("customer", "=", True)], required=True)
    customer_id = fields.Many2one("res.partner", "Destination", domain=[("active", "=", True), ("customer", "=", True)], required=True)
    dest_type = fields.Selection(DEST_TYPE, "Destination Type", required=True)
    so_number = fields.Char("SO Number")
    dn_number = fields.Char("DN Number")
    shipment_number = fields.Char("Shipment Number")

    total_rent = fields.Integer("Total Amount", compute="_get_total_pay", store=True)
    note = fields.Text("Note")

    line_ids = fields.One2many("dalsil.rent_truck.line", "parent_id", "Product")
    sangu_invoice_id = fields.Many2one("account.invoice", "Invoice Sangu", readonly="1")
    rent_invoice_id = fields.Many2one("account.invoice", "Invoice Rent", readonly="1")
    inv_invoice_id = fields.Many2one("account.invoice", "Customer Invoice", readonly="1")
    pur_invoice_id = fields.Many2one("account.invoice", "Vendor Bill", readonly="1")

    #################### Compute ####################
    @api.depends("line_ids", "line_ids.sub_total")
    def _get_total_pay(self):
        """
        Menghitung jumlah pembayaran
        """
        for record in self:
            record.total_rent = sum(record.line_ids.mapped("sub_total"))

    #################### State ####################
    @api.multi
    def to_open(self):
        """
        Ubah state menjadi open
        """
        for record in self:
            record = record.suspend_security()
            if record.state != STATE[0][0]:
                continue
            record._cstate(STATE[1][0])

    @api.multi
    def to_done(self):
        """
        Ubah state jadi done
        """
        for record in self:
            record = record.suspend_security()
            if record.state != STATE[1][0]:
                continue
            record._cstate(STATE[2][0])
            vals = {
                'partner_id': record.customer_id.business_partner_id.id,
                'invoice_line': tuple((0, 0, {
                    'product_id'
                    'name': 'Customer Invoice Item ({})'.format(line.calc_id.calc_number),
                    'quantity': 1.0,
                    'price_unit': line.amount
                }) for line in record.calc_ids)
            }
            invoice = self.env['account.invoice'].create(vals)

    @api.multi
    def to_cancel(self):
        """
        Ubah state jadi cancel
        """
        self._cstate(STATE[3][0])