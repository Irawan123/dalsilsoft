from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, date, time, timedelta

DEST_TYPE = (
    ("rent", _("Rent")),
    ("warehouse", _("Warehouse")),
    ("customer", _("Customer"))
)

class WizRentTruck(models.TransientModel):
    """
    Wizard model untuk mengisikan data2 yang dibutuhkan untuk membuat account invoice
    """
    _name = "dalsil.wiz_rent_truck"
    _inherit = "ss.wizard"
    _description = "Wizard Generate Account Invoice"

    rent_truck_id = fields.Many2one("dalsil.rent_truck", string="Rent Truck")
    dest_type = fields.Selection(DEST_TYPE, "Destination Type")
    
    sangu_payment_term_id = fields.Many2one('account.payment.term', string='Sangu Payment Terms')
    
    rent_payment_term_id = fields.Many2one('account.payment.term', string='Rent Payment Terms')

    inv_line_ids = fields.One2many("dalsil.wiz_rent_truck.line_inv", "parent_id", "Product")

    pur_line_ids = fields.One2many("dalsil.wiz_rent_truck.line_pur", "parent_id", "Product")

    #################### public ####################
    def show(self, rent_truck_id):
        """
        Tampilkan wizard ini
        
        :param rent_truck_id: Object/ID general expense
        """
        rent_truck_id = self.env["dalsil.rent_truck"].browse(rent_truck_id) if isinstance(rent_truck_id, int) else rent_truck_id
        lines = []
        for line_id in rent_truck_id.line_ids:
            lines.append([0, 0, {
                'product_id': line_id.product_id.id,
                'qty': line_id.qty
            }])
        return self.wizard_show("General Invoice", {
            "rent_truck_id": rent_truck_id.id,
            "dest_type": rent_truck_id.dest_type,
            "inv_line_ids": lines,
            "pur_line_ids": lines
        }, True)

    #################### private ####################
    @api.multi
    def _generate_sangu(self):
        """
        Generate Journal entry
        """
        setting = self.env["ir.model.data"].xmlid_to_object("dalsil_pkg_basic.dalsil_config")
        # setting = self.env['dalsil.wiz_config'].get_default_setting()
        vals = {
            'jenis_inv': "sangu",
            'partner_id': self.rent_truck_id.driver_id.id,
            'origin': self.rent_truck_id.name,
            'type': 'in_invoice',
            'payment_term_id': self.sangu_payment_term_id.id,
            'invoice_line': (0, 0, {
                'product_id': setting.product_sangu.id,
                'name': 'Sangu Driver Rent Truck No ({})'.format(self.rent_truck_id.name),
                'quantity': 1.0,
                'price_unit': setting.def_sangu
            })
        }
        self.rent_truck_id.sangu_invoice_id = self.env['account.invoice'].create(vals)

    @api.multi
    def _generate_rent(self):
        """
        Generate Journal entry
        """
        setting = self.env["ir.model.data"].xmlid_to_object("dalsil_pkg_basic.dalsil_config")
        # setting = self.env['dalsil.wiz_config'].get_default_setting()
        vals = {
            'jenis_inv': "rent",
            'partner_id': self.rent_truck_id.customer_rent_id.id,
            'origin': self.rent_truck_id.name,
            'type': 'out_invoice',
            'payment_term_id': self.rent_payment_term_id.id,
            'invoice_line': (0, 0, {
                'product_id': setting.product_rent.id,
                'name': 'Cost Rent Truck No ({})'.format(self.rent_truck_id.name),
                'quantity': 1.0,
                'price_unit': self.rent_truck_id.total_rent
            })
        }
        self.rent_truck_id.rent_invoice_id = self.env['account.invoice'].create(vals)

    @api.multi
    def _generate_purchase(self):
        """
        Generate Journal entry
        """
        vals = {
            'jenis_inv': "purchase",
            'partner_id': self.rent_truck_id.customer_rent_id.id,
            'origin': self.rent_truck_id.name,
            'type': 'in_invoice',
            'payment_term_id': self.rent_payment_term_id.id,
            'invoice_line': tuple((0, 0, {
                'product_id': line.product_id.id,
                'name': 'Cost Rent Truck No ({})'.format(self.rent_truck_id.name),
                'quantity': line.qty,
                'price_unit': line.unit_price
            }) for line in record.pur_line_ids)
        }
        self.rent_truck_id.pur_invoice_id = self.env['account.invoice'].create(vals)

    @api.multi
    def _generate_invoice(self):
        """
        Generate Journal entry
        """
        vals = {
            'jenis_inv': "invoice",
            'partner_id': self.rent_truck_id.customer_rent_id.id,
            'origin': self.rent_truck_id.name,
            'type': 'out_invoice',
            'payment_term_id': self.rent_payment_term_id.id,
            'invoice_line': tuple((0, 0, {
                'product_id': line.product_id.id,
                'name': 'Cost Rent Truck No ({})'.format(self.rent_truck_id.name),
                'quantity': line.qty,
                'price_unit': line.unit_price
            }) for line in record.inv_line_ids)
        }
        self.rent_truck_id.inv_invoice_id = self.env['account.invoice'].create(vals)

    #################### Button ####################
    def do_continue(self):
        """
        Membuatkan journal untuk pembayran expense
        """
        self.ensure_one()
        if self.dest_type == 'rent':
            self._generate_sangu()
            self._generate_rent()
        elif self.dest_type == 'warehouse':
            self._generate_sangu()
            self._generate_rent()
            self._generate_purchase()
        elif self.dest_type == 'customer':
            self._generate_sangu()
            self._generate_rent()
            self._generate_purchase()
            self._generate_invoice()

        return {}
