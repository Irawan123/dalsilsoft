odoo.define("dalsil.WebBranding", function (require) {
    var WebClient = require("web.WebClient");

    WebClient.include({
        init: function(parent, client_options) {
            this._super(parent, client_options);
            this.set('title_part', {"zopenerp": "DalSilSoft"});
        },
        update_logo: function(reload) {
            // do nothing
        }
    });
});

odoo.define('dalsil.WarnBranding',function (require) {
    "use strict";
    var CrashManager = require('web.CrashManager');
    var Dialog = require('web.Dialog');
    var core = require('web.core');

    var QWeb = core.qweb;
    var _t = core._t;

    CrashManager.include({
        rpc_error: function(error) {
            if (!this.active) {
                return;
            }
            if (this.connection_lost) {
                return;
            }

            if (error.data.name === "openerp.http.SessionExpiredException" || error.data.name === "werkzeug.exceptions.Forbidden") {
                this.show_warning({type: "Session Expired", data: { message: _t("Your DalSilSoft session expired. Please refresh the current web page.") }});
                return;
            }

            this._super.apply(this, arguments);
        },
        show_warning: function(error) {
            if (!this.active) {
                return;
            }
            new Dialog(this, {
                size: 'medium',
                title: "DalSil Soft " + (_.str.capitalize(error.type) || _t("Warning")),
                subtitle: error.data.title,
                $content: $('<div>').html(QWeb.render('CrashManager.warning', {error: error}))
            }).open();
        },
        show_error: function(error) {
            if (!this.active) {
                return;
            }
            new Dialog(this, {
                title: "DalSil Soft " + _.str.capitalize(error.type),
                $content: QWeb.render('CrashManager.error', {error: error})
            }).open();
        },
    });

    var RedirectWarningHandler = core.crash_registry.get("openerp.exceptions.RedirectWarning", true);
    RedirectWarningHandler.include({
        display: function() {
            var self = this;
            var error = this.error;
            error.data.message = error.data.arguments[0];

            new Dialog(this, {
                size: 'medium',
                title: "DalSil Soft " + (_.str.capitalize(error.type) || "Warning"),
                buttons: [
                    {text: error.data.arguments[2], classes : "btn-primary", click: function() {
                        window.location.href = '#action='+error.data.arguments[1];
                        self.destroy();
                    }},
                    {text: _t("Cancel"), click: function() { self.destroy(); }, close: true}
                ],
                $content: QWeb.render('CrashManager.warning', {error: error}),
            }).open();
        }
    });
});
