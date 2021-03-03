function getGroups(elem, selector) {
    return elem.parent().children(selector).text();
}

function groups_checked(groups, checked) {
    if(groups === undefined) {
        groups = "";
    };
    $('.btn-check').each(function() {
        if(groups.indexOf($(this).attr('name')) > -1 && checked) {
            $(this).prop('checked', checked);
        } else if(checked === false) {
            $(this).prop('checked', checked);
        };
    })
}

function addInputUserToForm(user) {
    let html = "<input type='hidden' name='username' value='";
    html += user;
    html += "' id='form-input-user'>";
    $('#form-change-groups').append(html);
}

function refreshGroups(data) {
    let id = data.split("/")[0];
    let text = data.split("/")[1];
    let selectorDashboard = '#user-detail-'+id;
    let selectorProfile = "#badges-groups"
    if ($(selectorDashboard).length > 0) {
        var elem = $(selectorDashboard).children('#d-groups')
    } else {
        var elem = $(selectorProfile)
    }
    let groups = text.split(";");
    elem.children(".group-name").remove();
    groups.forEach(function (group) {
        let html = "<span class='badge bg-primary group-name'>"
        html += group
        html += "</span>"
        elem.append(html)
    })
}

window.onload = function () {
    $(".d-edit-groups-link").click(function () {
        let groups = getGroups($(this), ".group-name");
        groups_checked(groups, true);
        let user = $(this).attr('name');
        addInputUserToForm(user);
    });
    $("#changeGroupsModal").on('hide.bs.modal', function () {
        $('#form-input-user').remove()
        groups_checked("", false);
    });
    $("#form-change-groups").submit(function (event) {
        event.preventDefault(event);
        let form = $(this);
        let username = $('#form-input-user').val();
        $.post("/change_groups", form.serialize())
            .done(function (data) {
                refreshGroups(data);
                // alert-success ?
            });
    });
}
