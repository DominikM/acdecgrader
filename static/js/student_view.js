function change_event(selector) {
    state.selected_event = parseInt(selector.value);

    // Now we need to update the table
    student_table.innerHTML = "";
    state.show_students = [];

    for (var i=0; i<data.students.length; i++) {
        if (parseInt(data.students[i].event_id) == state.selected_event) {
            // we check to see if the student is associated with the event, if so we throw them in the list of current students
            state.show_students.push(data.students[i]);

            // now we need to add it to the table

            // For name
            var student_f_name = document.createElement('td');
            student_f_name.innerHTML = data.students[i].first_name;

            var student_l_name = document.createElement('td');
            student_l_name.innerHTML = data.students[i].last_name;

            // For rank
            var student_rank = document.createElement('td');
            switch (data.students[i].rank) {
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

            student_table.appendChild(row);
        }
    }

    if (state.show_students.length == 0) {
            document.getElementsByTagName('table')[0].className = "ui celled fixed table";

            var row = document.createElement('tr');
            var item = document.createElement('td');
            item.innerHTML = 'There are no students assigned to this event!';
            item.colSpan = 5;

            row.appendChild(item);
            student_table.appendChild(row);
        }

}

function init_page() {
    for (var i=0; i<data.events.length; i++) {
        var new_event = document.createElement('option');
        new_event.value = data.events[i].id;
        new_event.innerHTML = data.events[i].name;
        event_selector.appendChild(new_event);
    }
    event_selector.selectedIndex = -1;
    $(event_selector).dropdown();
}