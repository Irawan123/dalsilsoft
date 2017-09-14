    odoo.define("dalsil.DisableNoContentHelp", function(require) {
    "use strict";

    var ListView = require("web.ListView");
    ListView.include({
        no_result: function() {
            this.options.action.help = undefined;
            this._super.apply(this);
        }
    });

    var KanbanView = require("web_kanban.KanbanView");
    KanbanView.include({
        render_no_content: function(fragment) {
            // do nothing
        }
    });

    return {
        "ListView": ListView,
        "KanbanView": KanbanView
    };
});
