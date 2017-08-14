from odoo import models, api


class ParentNestedSetModel(models.AbstractModel):
    """
    Model untuk update ``parent_left`` & ``parent_right`` dari sebuah model.
    """
    _name = "ss.parent"

    @api.model
    def recompute_parent(self, model_name):
        """
        Komputasi ulang field ``parent_left`` & ``parent_right``.

        :param model_name: Nama model untuk di recompute.
        """
        if self.env.uid != 1:
            return False

        return self.env[model_name]._parent_store_compute() or False
