from odoo import models, api


class Wizard(models.AbstractModel):
    """
    Model dasar untuk mempermudah operasi wizard.
    """
    _name = "ss.wizard"

    @api.model
    def show_dict(self, title, res_id=None, vals=None):
        """
        Mendapatkan dictionary default untuk menampilkan wizard.

        :param title: Judul dari wizard ini.
        :type title: basestring
        :param res_id: Id dari wizard untuk ditampilkan (optional).
        :type res_id: int
        :param vals: Dictionary data untuk mengubah setting.
        :type vals: dict
        """
        act = {
            "name": title,
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "view_mode": "form",
            "target": "new",
        }
        if res_id:
            act["res_id"] = res_id

        if vals:
            act.update(vals)

        return act

    @api.model
    def wizard_show(self, title, vals=None, nocreate=False):
        """
        Method untuk menampilkan wizard (kondisi object iwzard blm di buat).

        :param title: Judul dari wizard ini.
        :type title: basestring
        :param vals: Dictionary data untuk mengisi model wizard.
        :type vals: dict
        :param nocreate: Jangan create wizard di DB untuk ditampilkan / tampilkan tanpa id
        :type nocreate: bool
        """
        vals = vals or {}

        if nocreate:
            vals = {"default_{}".format(key): value for key, value in vals.items()}

            return self.show_dict(title, vals={"context": vals})

        obj = self.create(vals)

        return self.show_dict(title, obj.id)

    @api.multi
    def wizard_next(self, title, vals=None):
        """
        Method untuk menampilkan kembali wizard yang sudah ada (biasanya untuk process wizard selanjutnya).

        :param title: Judul dari wizard ini.
        :type title: basestring
        :param vals: Dictionary data untuk mengubah record wizard.
        :type vals: dict
        """
        self.ensure_one()

        # update wizard dengan vals
        if vals:
            self.write(vals)

        return self.show_dict(title, self.id)
