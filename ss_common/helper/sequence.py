from odoo import models, api


class Sequence(models.AbstractModel):
    """
    Wrapper untuk mempermudah penggunaan model ``ir.sequence``.
    """
    _name = "ss.sequence"

    # wrapper method
    @api.model
    def next_by_id(self, seq_id):
        """
        Wrapper method ``next_by_id`` dari ``ir.sequence``.

        :param seq_id: Id dari sequence untuk di dapatkan penomoran nya.
        :type seq_id: int
        :return: Penomoran.
        """
        return self.env['ir.sequence'].browse(seq_id).next_by_id()

    @api.model
    def next_by_extid(self, extid):
        """
        Sama seperti method ``next_by_id``, tetapi menggunakan external id.

        :param extid: External id dari sequence untuk di dapatkan penomoran nya (harus lengkap dengan nama module).
        :type extid: basestring
        :return: Penomoran.
        """
        res_id = self.env["ir.model.data"].xmlid_to_res_id(extid, True)

        return self.next_by_id(res_id)

    @api.model
    def next_by_code(self, code):
        """
        Wrapper method ``next_by_code`` dari ``ir.sequence``.

        :param code: Kode penomoran dari sequence.
        :type code: basestring
        :return: Penomoran.
        """
        return self.env['ir.sequence'].next_by_code(code)
