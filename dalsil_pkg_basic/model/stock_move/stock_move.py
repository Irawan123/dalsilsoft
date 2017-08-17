__author__ = "Michael PW"

from odoo import models, fields, api
from odoo.exceptions import ValidationError

STATE = (
    ("draft", "Draft"),
    ("done", "Done"),
    ("cancel", "Cancel")
)

class StockMove(models.Model):
    _name = "dalsil.stock_move"
    _inherit = "ss.model"
    _description = "Stock Move"
    _state_start = STATE[0][0]

    name = fields.Char("Stock Move No")
    source_loc_id = fields.Many2one("dalsil.location", "Lokasi Awal")
    dest_loc_id = fields.Many2one("dalsil.location", "Lokasi Tujuan")
    line_ids = fields.One2many("dalsil.stock_move.line", "parent_id", string="Detail Stock")
    note = fields.Text("Keterangan")
    state = fields.Selection(STATE, string="Status")
    purchase_id = fields.Many2one("dalsil.purchase", "Ref Purchase")
    done_uid = fields.Many2one("res.users", "Done By", readonly=True)
    dt_done = fields.Datetime("Done On", readonly=True)
    cancel_uid = fields.Many2one("res.users", "Canceled By", readonly=True)
    dt_cancel = fields.Datetime("Canceled On", readonly=True)
    cancel_reason = fields.Text("Reason for Canceled")

    @api.multi
    def to_done(self):
        for record in self:
            record = record.suspend_security()
            if record.state != 'draft':
                continue
            stock = self.env['dalsil.stock'].suspend_security()
            for line_id in record.line_ids:
                if record.source_loc_id:
                    stock.set_stock(line_id.product_id, record.source_loc_id, line_id.qty)
                if record.dest_loc_id:
                    stock.set_stock(line_id.product_id, record.dest_loc_id, line_id.qty)
            record.done_uid = record.env.uid
            record.dt_done = fields.Datetime.now()
            record.state = 'done'

    @api.multi
    def to_cancel(self, reason):
        for record in self:
            record = record.suspend_security()
            if record.state == 'done':
                stock = self.env['dalsil.stock'].suspend_security()
                for line_id in record.line_ids:
                    if record.source_loc_id:
                        stock.set_stock(line_id.product_id, record.source_loc_id, line_id.qty * -1)
                    if record.dest_loc_id:
                        stock.set_stock(line_id.product_id, record.dest_loc_id, line_id.qty * -1)
            record.cancel_uid = record.env.uid
            record.dt_cancel = fields.Datetime.now()
            record.cancel_reason = reason
            record.state = 'cancel'

    @api.multi
    def to_cancel_rejector(self):
        return self.env["ss.rejector"].show(
            self, "to_cancel", "Cancel Stock Move",
            "Untuk mengcancel Stock Move `{}`, berikan alasan:".format(self.name)
        )