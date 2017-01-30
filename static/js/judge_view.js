function change_event(selector) {
    elements.add_judge.style.visibility = 'visible';
    state.selected_event = parseInt(selector.value);
    // now we need to add it to the table
    refresh_judges();
    update_table();
}

function refresh_judges() {
    state.show_judges = [];
    for (var i=0; i<data.judges.length; i++) {
        if (parseInt(data.judges[i].event_id) == state.selected_event) {
            // we check to see if the judge is associated with the event, if so we throw them in the list of current judges
            state.show_judges.push(i);
        }
    }
}

function update_table() {
    judge_table.innerHTML = "";

    // check to see if current showen judges is non zero
    if (state.show_judges.length == 0) {
        document.getElementsByTagName('table')[0].className = "ui celled fixed table";

        var row = document.createElement('tr');
        var item = document.createElement('td');
        item.innerHTML = 'There are no judges assigned to this event!';
        item.colSpan = 2;

        row.appendChild(item);
        judge_table.appendChild(row);
        return;
    }

    for (var i=0; i<state.show_judges.length; i++) {
        var cur_judge = data.judges[state.show_judges[i]];

        // For name
        var judge_f_name = document.createElement('td');
        judge_f_name.innerHTML = cur_judge.first_name;

        var judge_l_name = document.createElement('td');
        judge_l_name.innerHTML = cur_judge.last_name;

        var judge_pass = document.createElement('td');
        judge_pass.innerHTML = cur_judge.password;

        var judge_user = document.createElement('td');
        judge_user.innerHTML = cur_judge.username;

        document.getElementsByTagName('table')[0].className = "ui celled fixed selectable table";

        var row = document.createElement('tr');
        row.appendChild(judge_f_name);
        row.appendChild(judge_l_name);
        row.appendChild(judge_user);
        row.appendChild(judge_pass);

        row.onclick = (
            function(val) {
                return function () {
                    edit_row(val);
            }
        })(i) ;

        judge_table.appendChild(row);
    }
}

function edit_row(judge) {
    if (state.selected_judge == null) {
        state.selected_judge = judge;

        // we need to get a list of all the rows then select the right one
        var selected_row = judge_table.getElementsByTagName('tr')[judge];
        selected_row.className = "active";

        var cells = selected_row.getElementsByTagName('td');

        // empty all the cells except user and pass
        for (var i = 0; i < cells.length - 2; i++)
            cells[i].innerHTML = "";

        var sel_judge = data.judges[state.show_judges[state.selected_judge]];

        elements.first_name_input = cells[0]
            .appendChild(document.createElement('div'))
            .appendChild(document.createElement('input'));

        elements.first_name_input.value = sel_judge.first_name;

        elements.last_name_input = cells[1]
            .appendChild(document.createElement('div'))
            .appendChild(document.createElement('input'));

        elements.last_name_input.value = sel_judge.last_name;

        var input_divs = selected_row.getElementsByTagName('div');
        input_divs[0].className = 'ui input'; // first name
        input_divs[1].className = 'ui input'; // last name

        // now let's add the buttons to the left of the row

        var row_loc = selected_row.getBoundingClientRect();
        
        icons_div.style.top = row_loc.top + document.body.scrollTop + 'px';
        icons_div.style.height = icons_div.style.lineHeight = (row_loc.bottom - row_loc.top) + 'px';
        icons_div.style.right = row_loc.right + 'px';
        icons_div.style.visibility = "visible";

    }
}

function unedit_row() {
    state.selected_judge = null;
    icons_div.style.visibility = "hidden";
    refresh_judges();
    update_table();
}

function show_delete_modal() {
    delete_judge_modal.modal('show');
}

function show_add_modal() {
    add_judge_modal.modal('show');
}

function remove_add_model() {
    $("#add-judge-form").form('clear');
    $("#add-judges-file").form('clear');
}

function save_judge() {
    // TODO: save request
    var judge = data.judges[state.show_judges[state.selected_judge]];
    var n_first_name = elements.first_name_input.value;
    var n_last_name = elements.last_name_input.value;
    $.post(
        data.urls.edit,
        {
            id: judge.id,
            first_name: n_first_name,
            last_name: n_last_name,
        },
        function (result) {
            if (result.result == 'fail') {
                console.error(result.message);
            } else if (result.result == 'success') {
                judge.first_name = n_first_name;
                judge.last_name = n_last_name;
                unedit_row();
            } else {
                console.error('Something went wrong that none of us prepared for.');
            }
        }
    );
    unedit_row();
}

function delete_judge() {
    $.post(
        data.urls.delete,
        {id: data.judges[state.show_judges[state.selected_judge]].id},
        function (result) {
            if (result.result == 'fail') {
                console.error(result.message);
            } else if (result.result == 'success') {
                data.judges.splice(state.selected_judge, 1); // remove from data
                unedit_row();
            } else {
                console.error('Something went wrong that none of us prepared for.')
            }
        }
    );
}

function add_judge() {
    file_input = document.getElementById('judge-csv');
    if (file_input.value != '') {
        var judges_data = new FormData();
        judges_data.append('event', state.selected_event);
        console.log(document.getElementById('judge-csv').files[0]);
        judges_data.append('file', document.getElementById('judge-csv').files[0]);
        
        $.ajax({
            type: 'post',
            url: data.urls.bulk_create,
            data: judges_data,
            success: function (result) {
                if (result.result == 'success') {
                    data.judges = data.judges.concat(result.judges);
                    refresh_judges();
                    update_table();
                    remove_add_model();
                    return true;
                } else {
                    console.error(result.message);
                    return false;
                }
            },
            processData: false,
            contentType: false
        })


    } else {
        form = $('#add-judge-form');
        inputs = form.find('.field');
        console.log(inputs);
        if (form[0].checkValidity()) {
            $("input[name='event']").val(state.selected_event);
            form.ajaxSubmit({
                url: data.urls.create,
                type:'post',
                success: function(result) {
                    if (result.result == 'success') {
                        console.log(result.judge);
                        data.judges.push(result.judge);
                        refresh_judges();
                        update_table();
                        remove_add_model();
                        return true
                    } else {
                        console.error(result.message);
                        return false
                    }
                }
            });
        } else {
            for (var i = 0; i<(inputs.length-1); i++){
                $(inputs[i]).addClass('error');
            }
            return false;
        }

    }
}

function init_page() {
    for (var i=0; i<data.events.length; i++) {
        var new_event = document.createElement('option');
        new_event.value = data.events[i].id;
        new_event.innerHTML = data.events[i].name;
        event_selector.appendChild(new_event);
    }

    var icons = icons_div.getElementsByTagName('i');
        icons[0].onclick = save_judge;
        icons[1].onclick = show_delete_modal;
        icons[2].onclick = unedit_row;

    delete_judge_modal
        .modal({
            onApprove: delete_judge
        });

    add_judge_modal
        .modal({
            onApprove: add_judge,
            onDeny: remove_add_model
        });

    event_selector.selectedIndex = -1;
    $(event_selector).dropdown();
}