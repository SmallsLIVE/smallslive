EventForm = {
    SITE_URL: "",
    fixTableWidths: function (selector) {
        $(selector).find('td').each(function () {
            $(this).css('width', $(this).width() + 'px');
        });
    },
    cloneMore: function (selector, type) {
        var newElement = $artist_row.clone(true);
        var $total = $('#id_' + type + '-TOTAL_FORMS');
        var total = $total.val();
        newElement.find(':input').each(function () {
            if ($(this).attr('id')) {
                var name = $(this).attr('name').replace('-0-', '-' + total + '-');
                var id = 'id_' + name;
                $(this).attr({'name': name, 'id': id}).val('').removeAttr('checked');
            }
        });
        newElement.find('.sort_order_field').val(total);
        total++;
        $total.val(total);
        $(selector).after(newElement);
        $(selector).find("select").selectize({
            create: false
        });
    },
    addSlotButtons: function(dayOfTheWeek){
        $slotButtons = $('.slot-buttons');
        $slotButtons.html("");
        var buttons = [];
        var todaysSchedule = show_times[dayOfTheWeek];
        $.each(todaysSchedule, function(idx, val) {
            var button = $("<input>", {
                type: "button",
                class: "btn btn-success slot",
                "data-time": val[0],
                title: val[1],
                value: val[2]
            });
            buttons.push(button, " ");
        });
        $slotButtons.append(buttons);
    },
    init: function () {
        $artist_row = $(".formset_table tbody tr:last").clone(true);

        $(".formset_table select").selectize({
            create: false
        });

        // Dynamically sets the default instrument for an artist
        $(document).on('change', '.artist_field', function (e) {
            var $role_field = $(e.currentTarget).parent().next().find("select");
            var value = $(e.currentTarget).val();
            $.get("//" + EventForm.SITE_URL + "/artists/" + value + "/instrument_ajax/", function (data) {
                $role_field[0].selectize.setValue(data);
            });
        });

        var $start = $('#id_start');
        var $end = $('#id_end');
        var date_format = "MM/DD/YYYY H:mm A";
        $start.datetimepicker({
            sideBySide: true,
            minuteStepping: 5,
            defaultDate: moment("19:00", "H:mm")
        });
        $end.datetimepicker({
            sideBySide: true,
            minuteStepping: 5,
            defaultDate: moment("20:00", "H:mm")
        });
        $start.on('dp.hide', function (ev) {
            // auto set event end to 1 hour later
            var end = moment($start.val()).add(1, 'hours').format(date_format);
            $end.data("DateTimePicker").setDate(end);
            EventForm.addSlotButtons(moment($start.val()).isoWeekday());
        });
        this.fixTableWidths('.formset_table');


        $('.formset_table tbody').sortable({
            // update the sort_order field based on the order in the DOM
            update: function (event, ui) {
                $(".sort_order_field").each(function (index) {
                    $(this).val(index);
                })
            }
        });

        this.addSlotButtons(moment().isoWeekday());

        $('#add_more').click(function () {
            EventForm.cloneMore('.formset_table tbody tr:last', 'artists_gig_info');
            EventForm.fixTableWidths('.formset_table');
        });

        $(document).on("click", ".artist_remove", function (e) {
            var $total = $('#id_artists_gig_info-TOTAL_FORMS');
            var total = $total.val();
            $(this).parents('tr').remove();
            total--;
            $total.val(total);
            EventForm.fixTableWidths('.formset_table');
            return false;
        });

        $('.slot-buttons').on("click", ".slot", function () {
            var times = $(this).data('time').split('-');
            var start, end;
            if (!$start.val()) {
                start = moment(times[0], "H:mm");
            }
            else {
                var split_start_time = times[0].split(':');
                start = moment($start.val(), date_format);
                start.hour(parseInt(split_start_time[0]));
                start.minutes(parseInt(split_start_time[1]));
            }

            if (!$end.val()) {
                end = moment(times[1], "H:mm");
            }
            else {
                var split_end_time = times[1].split(':');
                end = moment($start.val(), date_format);
                end.hour(parseInt(split_end_time[0]));
                end.minutes(parseInt(split_end_time[1]));
            }

            // if both start and end are early in the morning, add 1 day to the start and end date,
            // otherwise, if only the end is after midnight, add 1 day to the end
            if (start.hour() < 6 && end.hour() < 6) {
                start.add('days', 1);
                end.add('days', 1);
            }
            else if (start.isAfter(end)) {
                end.add('days', 1);
            }
            $start.data("DateTimePicker").setDate(start.format(date_format));
            $end.data("DateTimePicker").setDate(end.format(date_format));
        });

        $("#id_title").focus(function() {
            if(! $(this).val()) {
                var title = $(".artist_field div.item").first().text();
                var remaining_artists = $(".artist_field div.item").not(":first");
                if (remaining_artists.length > 0) {
                    title += " w/ ";
                    remaining_artists.not(':last').each(function() {
                        title += $(this).text() + ", ";
                    });
                    title += remaining_artists.last().text();
                }
                $(this).val(title);
            }
        });
    }

};