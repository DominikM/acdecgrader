function change_event(selector) {
    elements.add_student.style.visibility = 'visible';
    state.selected_event = parseInt(selector.value);
    // now we need to add it to the table
    refresh_students();
    update_table();
}

function refresh_students() {
    state.show_students = [];
    for (var i=0; i<data.students.length; i++) {
        if (parseInt(data.students[i].event_id) == state.selected_event) {
            // we check to see if the student is associated with the event, if so we throw them in the list of current students
            state.show_students.push(i);
        }
    }
}

function update_table() {
    student_table.innerHTML = "";

    // check to see if current showen students is non zero
    if (state.show_students.length == 0) {
        document.getElementsByTagName('table')[0].className = "ui celled fixed table";

        var row = document.createElement('tr');
        var item = document.createElement('td');
        item.innerHTML = 'There are no students assigned to this event!';
        item.colSpan = 5;

        row.appendChild(item);
        student_table.appendChild(row);
        return;
    }

    for (var i=0; i<state.show_students.length; i++) {
        var cur_student = data.students[state.show_students[i]];

        // For name
        var student_f_name = document.createElement('td');
        student_f_name.innerHTML = cur_student.first_name;

        var student_l_name = document.createElement('td');
        student_l_name.innerHTML = cur_student.last_name;

        // For rank
        var student_rank = document.createElement('td');
        switch (cur_student.rank) {
            case 0:
                student_rank.innerHTML = 'Varsity';
                break;

            case 1:
                student_rank.innerHTML = 'Scholastic';
                break;

            case 2:
                student_rank.innerHTML = 'Honors';
                break;
        }
        student_rank.colSpan = 3;

        document.getElementsByTagName('table')[0].className = "ui celled fixed selectable table";

        var row = document.createElement('tr');
        row.appendChild(student_f_name);
        row.appendChild(student_l_name);
        row.appendChild(student_rank);

        row.onclick = (
            function(val) {
                return function () {
                    edit_row(val);
            }
        })(i) ;

        student_table.appendChild(row);
    }
}

function edit_row(student) {
    if (state.selected_student == null) {
        state.selected_student = student;

        // we need to get a list of all the rows then select the right one
        var selected_row = student_table.getElementsByTagName('tr')[student];
        selected_row.className = "active";

        var cells = selected_row.getElementsByTagName('td');

        // empty all the cells
        for (var i = 0; i < cells.length; i++)
            cells[i].innerHTML = "";

        var sel_student = data.students[state.show_students[state.selected_student]];

        elements.first_name_input = cells[0]
            .appendChild(document.createElement('div'))
            .appendChild(document.createElement('input'));

        elements.first_name_input.value = sel_student.first_name;

        elements.last_name_input = cells[1]
            .appendChild(document.createElement('div'))
            .appendChild(document.createElement('input'));

        elements.last_name_input.value = sel_student.last_name;

        elements.rank_select = cells[2]
            .appendChild(document.createElement('select'));

        var ranks = ['Varsity', 'Scholastic', 'Honors'];

        for (var i=0; i < ranks.length; i++) {
            var rank_option = elements.rank_select.appendChild(document.createElement('option'));
            rank_option.value = i;
            rank_option.innerHTML = ranks[i];
        }

        elements.rank_select.selectedIndex = sel_student.rank;

        var input_divs = selected_row.getElementsByTagName('div');
        input_divs[0].className = 'ui input'; // first name
        input_divs[1].className = 'ui input'; // last name
        $(elements.rank_select).dropdown();
        cells[2].style.overflow = 'visible';

        // now let's add the buttons to the left of the row

        var row_loc = selected_row.getBoundingClientRect();
        
        icons_div.style.top = row_loc.top + document.body.scrollTop + 'px';
        icons_div.style.height = icons_div.style.lineHeight = (row_loc.bottom - row_loc.top) + 'px';
        icons_div.style.right = row_loc.right + 'px';
        icons_div.style.visibility = "visible";

    }
}

function unedit_row() {
    state.selected_student = null;
    icons_div.style.visibility = "hidden";
    refresh_students();
    update_table();
}

function show_delete_modal() {
    delete_student_modal.modal('show');
}

function show_add_modal() {
    add_student_modal.modal('show');
    rank_dropdown.dropdown();
}

function save_student() {
    // TODO: save request
    var student = data.students[state.show_students[state.selected_student]];
    var n_first_name = elements.first_name_input.value;
    var n_last_name = elements.last_name_input.value;
    var n_rank = parseInt(elements.rank_select.value);
    $.post(
        data.urls.edit,
        {
            id: student.id,
            first_name: n_first_name,
            last_name: n_last_name,
            rank: n_rank
        },
        function (result) {
            if (result.result == 'fail') {
                console.error(result.message);
            } else if (result.result == 'success') {
                student.first_name = n_first_name;
                student.last_name = n_last_name;
                student.rank = n_rank;
                unedit_row();
            } else {
                console.error('Something went wrong that none of us prepared for.');
            }
        }
    );
    unedit_row();
}

function delete_student() {
    $.post(
        data.urls.delete,
        {id: data.students[state.show_students[state.selected_student]].id},
        function (result) {
            if (result.result == 'fail') {
                console.error(result.message);
            } else if (result.result == 'success') {
                data.students.splice(state.selected_student, 1); // remove from data
                unedit_row();
            } else {
                console.error('Something went wrong that none of us prepared for.')
            }
        }
    );
}

function add_student() {
    file_input = document.getElementById('student-csv');
    if (file_input.value != '') {

    } else {
        form = $('#add-student-form');
        inputs = form.find('.field');
        console.log(inputs);
        if (form[0].checkValidity()) {
            $("input[name='event']").val(state.selected_event);
            form.ajaxSubmit({
                url: data.urls.create,
                type:'post',
                success: function(result) {
                    if (result.result == 'success') {
                        console.log(result.student);
                        data.students.push(result.student);
                        refresh_students();
                        update_table();
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
        icons[0].onclick = save_student;
        icons[1].onclick = show_delete_modal;
        icons[2].onclick = unedit_row;

    delete_student_modal
        .modal({
            onApprove: delete_student
        });

    add_student_modal
        .modal({
            onApprove: add_student
        });

    event_selector.selectedIndex = -1;
    $(event_selector).dropdown();
}