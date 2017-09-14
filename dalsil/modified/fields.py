from odoo.fields import Field

super_get_description = Field.get_description


def get_description(self, env):
    """
    Hapus field help di hasil description
    """
    result = super_get_description(self, env)
    if "isme.cp" in env:
        result.pop("help", None)

    return result


Field.get_description = get_description
