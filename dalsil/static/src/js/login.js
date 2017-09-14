function debranding_odoo() {
    // Logo
    var logo = $("div.text-center:first");
    if(logo.length) {
        // logo found, website not installed
        logo.html('<a href="http://dalsil.id/" target="_blank"><img src="/dalsil/static/src/img/isme_soft_277X189.png"/></a>');

        // debrand link
        var links = $("div.text-center:eq(1)>a");
        var  link = undefined;
        if(links.length == 1) {// manage database disabled
            link = $(links[0]);
        } else {// manage database enabled
            link = $(links[1]);
        }
        link.attr("href", "http://dalsil.co.id/");
        link.html('Product of <span style="color: #9E0B0F; font-style: italic">DALSIL</span');

        return;
    }

    logo = $("a.logo");
    if(logo.length) {
        // Logo on website found
        logo.attr("href", "http://dalsil.id/");
        logo.attr("target", "_blank");
        logo.html('<img src="/dalsil/static/src/img/isme_soft_277X189.png"/>');

        return;
    }
}

$(function() {
    debranding_odoo();
});
