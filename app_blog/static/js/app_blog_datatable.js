
function add_sort_select(target) {
    let thead_table = $('#articles-list > thead > tr');
    let select = '<select id="select-sort-articles" class="form-select" aria-label="Trier par ...">';
    var content = '<div class="col-sm-12 col-md-12"><div id="sort-div" class="dataTables_filter"><label>Trier par : ' + select;
    let thead_table_children = thead_table.children();
    thead_table_children.each(function (i) {
        let text = $(this).text();
        let option = '<option value="' + i + '_asc">' + text + ' &#8595;</option>';
        let option2 = '<option value="' + i + '_desc">' + text + ' &#8593;</option>';
        content += option + option2;
    });
    content += "</select></label>";
    target.prepend(content);
}

window.addEventListener('load', function () {
    var settings_datatable = $("#articles-list_wrapper > div:nth-child(1)");
    add_sort_select(settings_datatable);
    $('#select-sort-articles').change(function (e) {
        // e.preventDefaults(e);
        let val = $(this).val();
        let new_order = val.split("_");
        let table = $('#articles-list').DataTable();
        table.order(new_order);
        table.draw();
    })
});
