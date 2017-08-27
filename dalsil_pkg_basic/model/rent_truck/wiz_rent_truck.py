from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime, date, time, timedelta

class WizRentTruck(models.TransientModel):
    """
    Wizard model untuk mengisikan data2 yang dibutuhkan untuk membuat account invoice
    """
    _name = "dalsil.wiz_rent_truck"
    _inherit = "ss.wizard"
    _description = "Wizard Generate Account Invoice"

    rent_truck_id = fields.Many2one("dalsil.rent_truck", string="Rent Truck")
    sangu_payment_term_id = fields.Many2one('account.payment.term', string='Sangu Payment Terms', required=True)
    
    rent_payment_term_id = fields.Many2one('account.payment.term', string='Rent Payment Terms', required=True)

    #################### public ####################
    def show(self, rent_truck_id):
        """
        Tampilkan wizard ini
        
        :param rent_truck_id: Object/ID general expense
        """
        rent_truck_id = self.env["dalsil.rent_truck"].browse(rent_truck_id) if isinstance(rent_truck_id, int) else rent_truck_id

        return self.wizard_show("General Invoice", {
            "rent_truck_id": rent_truck_id.id
        }, True)

    #################### private ####################
    @api.multi
    def _generate_sangu(self):
        """
        Generate Journal entry
        """
        setting = self.env['dalsil.wiz_config'].get_default_setting()
        vals = {
            'partner_id': self.rent_truck_id.driver_id.id,
            'origin': self.rent_truck_id.name,
            'type': 'in_invoice',
            'payment_term_id': self.sangu_payment_term_id.id,
            'invoice_line': (0, 0, {
                'product_id': setting['product_sangu'],
                'name': 'Sangu Driver Rent Truck No ({})'.format(self.rent_truck_id.name),
                'quantity': 1.0,
                'price_unit': setting['def_sangu']
            })
        }
        self.rent_truck_id.sangu_invoice_id = self.env['account.invoice'].create(vals)

    @api.multi
    def _generate_rent(self):
        """
        Generate Journal entry
        """
        setting = self.env['dalsil.wiz_config'].get_default_setting()
        vals = {
            'partner_id': self.rent_truck_id.customer_rent_id.id,
            'origin': self.rent_truck_id.name,
            'type': 'out_invoice',
            'payment_term_id': self.rent_payment_term_id.id,
            'invoice_line': (0, 0, {
                'product_id': setting['product_rent'],
                'name': 'Cost Rent Truck No ({})'.format(self.rent_truck_id.name),
                'quantity': 1.0,
                'price_unit': self.rent_truck_id.total_rent
            })
        }
        self.rent_truck_id.rent_invoice_id = self.env['account.invoice'].create(vals)

    #################### Button ####################
    def do_continue(self):
        """
        Membuatkan journal untuk pembayran expense
        """
        self.ensure_one()
        if self.rent_truck_id.dest_type == 'rent':
            self._generate_sangu()
            self._generate_rent()
        elif self.rent_truck_id.dest_type == 'warehouse':
            self._generate_sangu()
            self._generate_rent()
            # self._generate_purchase()
        elif self.rent_truck_id.dest_type == 'customer':
            self._generate_sangu()
            self._generate_rent()
            # self._generate_purchase()
            # self._generate_invoice()
        # self.env["isme.expense.general.pay"]._ccreate({
        #     "company_id": self.gen_exp_id.company_id.id,
        #     "payment_type": "outbound",
        #     "name": self.memo,
        #     "journal_id": self.journal_id.id,
        #     "amount": self.amount,
        #     "pay_date": self.pay_date,
        #     "gen_exp_id": self.gen_exp_id.id,
        #     "partner_id": self.gen_exp_id.partner_id.id or None,
        # }).to_post()
        # self._generate_journal_entry()
        # self.gen_exp_id.to_pay()

        return {}
