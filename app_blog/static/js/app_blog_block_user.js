function refreshActive(link, is_active) {
    link.children().removeClass(["bi-unlock-fill", "bi-lock-fill"])
    if (is_active === "True") {
        link.children().addClass("bi-lock-fill");
        link.children().prop('innerText', "Actif");
    } else {
        link.children().addClass("bi-unlock-fill");
        link.children().prop('innerText', "Inactif");
    }
}

window.addEventListener('load', function () {
    $(".block-user-link").click(function (event) {
        event.preventDefault(event);
        var block_link = $(this);
        $.get($(this).attr('href'))
            .done(function (data) {
                if (data.split("/").length === 2) {
                    let is_active = data.split("/")[1];
                    refreshActive(block_link, is_active); 
                }
            });
    });
});
