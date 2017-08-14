from odoo import models, fields, api


class Rejector(models.TransientModel):
    """
    Wizard untuk ditampilkan ketika melakukan reject/  cancel yg mebutuhkan alasan.
    """
    _name = "ss.rejector"
    _inherit = "ss.wizard"

    res_model = fields.Char("Model Name", required=True)
    res_id = fields.Integer("Data Id", required=True)

    description = fields.Text("Description")
    callback = fields.Char("Post Action", required=True)

    reason = fields.Text("Reason")

    @api.model
    def show(self, record, callback, title="Reject / Cancel", description=False):
        """
        Menampilkan rejector.

        :param record: Object record yg digunakan sebagai callback & sumber data.
        :param callback: Method yang dipanggil ketika rejector di lanjutkan.
                         Method ini harus bisa menerima 1 parameter, untuk alasan penolakan.
                         Nantinya method ini yg seharus nya melakukan update.
        :param title: Judul rejector
        :param description: Keterangan pada rejector
        """
        vals = {
            "res_model": record._name,
            "res_id": record.id,
            "callback": callback,
            "description": description,
        }

        return self.wizard_show(title, vals)

    @api.multi
    def do_continue(self):
        """
        Tombol continue, untuk melakukan `reject / cancel` model.
        """
        obj = self.env[self.res_model].browse(self.res_id)

        return getattr(obj, self.callback)(self.reason)
