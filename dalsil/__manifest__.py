{
    "name": "DalSilSoft Base Module",
    "description": "Module dasar yang mengubah odoo menjadi dalsilsoft",
    "version": "10.0.0.0.1",
    "author": "DalSil",
    "license": "AGPL-3",
    "category": "DalSil",
    "depends": [
        "web", "web_kanban", "mail",
        "disable_odoo_online", "web_no_bubble",
        "ss_common"
    ],
    "data": [
        "view/inherit/branding.xml",
        "view/control_panel.xml",

        "view/menu.xml",
    ],
    "qweb": ["static/src/xml/*.xml"]
}
