from base64 import b64encode, b64decode

from odoo import models, fields, api
from odoo.addons.web.controllers.main import serialize_exception, content_disposition
from odoo.http import Controller, route, request

BINARY_URL = "/web/ss/download"


class Downloader(models.TransientModel):
    """
    Model untuk melakukan download
    """
    _name = "ss.download"

    data = fields.Binary(required=True)

    @api.model
    def download_from(self, model, field, id, filename, target="new", filename_as_field=""):
        """
        Mengembalikan url untuk download.

        :param model: model yang dicari.
        :param field: Field yang berisi data.
        :param id: id record yg memiliki data.
        :param filename: Nama file untuk download.
        :param target: Target download, apakah membuat tab baru (`new`) atau langsung keluar (`self`)
        :param filename_as_field: Apakah filename merupakan nama field? (default False)
        """
        filename = filename if filename_as_field else filename

        return {
            "type": "ir.actions.act_url",
            "url": "{}?model={}&id={}&field={}&fname={}&fnamefield={}".format(
                BINARY_URL, model, id, field, filename, filename_as_field
            ),
            "target": target
        }

    @api.model
    def download(self, filename, data, target="new"):
        """
        Proses download data menggunakan controller custom di bawah.

        :param filename: Nama file.
        :param data: Data file yang akan di upload (blm di encode base64).
        :param target: Target download, apakah membaut tab baru (`new`) atau langsung keluar (`self`)
        """
        obj = self.create({"data": b64encode(data)})

        return self.download_from(self._name, "data", obj.id, filename, target)


class BinaryDownload(Controller):
    """
    Controller untuk download binary.
    """

    @route(BINARY_URL)
    @serialize_exception
    def download_binary(self, model, id, field, fname, fnamefield, **kwargs):
        """
        Route http untuk download binary
        """
        fs = [field]
        if fnamefield:
            fs.append(fname)
        record = request.env[model].browse(int(id)).read(fs)[0]
        data = b64decode(record.get(field, False) or False)
        filename = record.get(fname, "unknown") if fnamefield else fname

        if not data:
            return request.not_found()

        return request.make_response(
            data,
            [
                ('Content-Type', 'application/octet-stream'),
                ('Content-Disposition', content_disposition(filename))
            ]
        )
