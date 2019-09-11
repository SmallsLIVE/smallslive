EventForm = {
  SITE_URL: "",
  selectedDate: "",
  fixTableWidths: function(table) {
    table.find("td").each(function() {
      $(this).css("width", $(this).width() + "px");
    });
  },
  cloneMore: function(source, destination, type) {
    var newElement = source.clone(false);
    var $total = $("#id_" + type + "-TOTAL_FORMS");
    var total = $total.val();
    newElement.find(":input").each(function() {
      if ($(this).attr("id")) {
        var name = $(this)
          .attr("name")
          .replace("-0-", "-" + total + "-");
        var id = "id_" + name;
        $(this)
          .attr({
            name: name,
            id: id
          })
          .val("")
          .removeAttr("checked");
      }
    });
    newElement.find(".sort_order_field").val(total);
    total++;
    $total.val(total);
    if (destination) {
      destination.after(newElement);
    }
    newElement.find("select").selectize({
      create: false
    });
    newElement.find(".artist_remove").on("click", function() {
      $(this)
        .parents("tr")
        .remove();
      return false;
    });

    return newElement;
  },
  addSlotButtons: function(dayOfTheWeek) {
    $slotButtons = $(".slot-buttons");
    $slotButtons.html("");
    var buttons = [];
    var todaysSchedule = show_times;
    $.each(todaysSchedule, function(idx, val) {
      var button = $("<input>", {
        type: "button",
        class: "btn btn-success slot",
        "data-time": val["set-starts"],
        title: val["set-title"],
        value: val["set-redeable-starts"],
        "data-set-duration": val["set-duration"],
        "data-venue": val["set-venue"]
      });
      buttons.push(button, " ");
    });
    $slotButtons.append(buttons);
    $(".btn.btn-success.slot").hide();
  },
  initDateTimeFunctionality: function() {
    var date_format = "MM/DD/YYYY HH:mm:ss";
    var $date = $("#id_date");
    var $start = $("#id_start");
    var $end = $("#id_end");

    $date.datetimepicker({
      sideBySide: true,
      pickTime: false,
      autoclose: true,
      format: "YYYY-MM-DD"
    });
    $date.datetimepicker("update");

    EventForm.selectedDate = moment($start.attr("value"));

    var propagateStart = function(start) {
      var redrawSlotButtons =
        EventForm.selectedDate.isoWeekday() !== start.isoWeekday();
      var oldEnd = moment($end.data("DateTimePicker").getDate());
      EventForm.selectedDate = start;

      // auto set event end to 1 hour later
      var newEnd = moment(
        new Date(
          start.year(),
          start.month(),
          start.date(),
          oldEnd.hour(),
          oldEnd.minute()
        )
      );

      // If start is before the midnight adjust end if necessary
      if (start.hour() >= 6) {
        if (newEnd.hour() > 0 && newEnd.hour() < 6) {
          newEnd = moment(newEnd).add(1, "d");
        }
      }

      var end = newEnd.format(date_format);
      $end.data("DateTimePicker").setDate(end);
    };

    $start.on("dp.hide", function(ev) {
      // save the selected date so that slot buttons work correctly
      var start = $(this)
        .data("DateTimePicker")
        .getDate();

      propagateStart(start);
      // $(this).data("DateTimePicker").show();
      return false;
    });

    // fix for not showing the widget on every click on input
    $end.on("dp.hide", function(ev) {
      $(this)
        .data("DateTimePicker")
        .show();
      return false;
    });

    $date.on("dp.change", function(ev) {
      var start = moment(
        $(this)
          .data("DateTimePicker")
          .getDate()
      );
      var oldStart = moment(EventForm.selectedDate);

      var newStart = moment(
        new Date(
          start.year(),
          start.month(),
          start.date(),
          oldStart.hour(),
          oldStart.minute()
        )
      );

      // If current start is after midnight
      if (oldStart.hour() > 0 && oldStart.hour() < 6) {
        newStart = moment(newStart).add(1, "d");
      }

      $start.data("DateTimePicker").setDate(newStart);
      propagateStart(newStart);

      return false;
    });

    $(".slot-buttons").on("click", ".slot", function() {
      var times = $(this).data("time").split("-");
      var start, end;

      let setDuration = $(this).data("set-duration");
      var startDate = $("#id_start");
      var endDate = $("#id_end");

      if (!startDate.val()) {
        start = moment(times[0], "H:mm");
      } else {
        var split_start_time = times[0].split(":");
        start = EventForm.selectedDate.clone();
        start.hour(parseInt(split_start_time[0]));
        start.minutes(parseInt(split_start_time[1]));
      }

      if (times[1]) {
        if (!endDate.val()) {
          end = moment(times[1], "H:mm");
        } else {
          var split_end_time = times[1].split(":");
          end = EventForm.selectedDate.clone();
          end.hour(parseInt(split_end_time[0]));
          end.minutes(parseInt(split_end_time[1]));
        }
      }

      // if both start and end are early in the morning, add 1 day to the start and end date,
      // otherwise, if only the end is after midnight, add 1 day to the end
      if (times[1]) {
        if (start.hour() < 6 && end.hour() < 6) {
          start.add("days", 1);
          end.add("days", 1);
        } else if (start.isAfter(end)) {
          end.add("days", 1);
        }
      }

      startDate.data("DateTimePicker").setDate(start.format(date_format));
      if (times[1]) {
        endDate.data("DateTimePicker").setDate(end.format(date_format));
      }
      EventForm.propagateSets(start, end, setDuration);
    });

    this.addSlotButtons(moment().isoWeekday());
  },
  configureTimePicker: function(firstRow) {
    firstRow.find("input.timeinput").each(function() {
      $(this).datetimepicker({
        pickDate: false,
        minuteStepping: 15,
        pickerPosition: "bottom-right",
        format: "hh:mm A",
        autoclose: true,
        showMeridian: true,
        startView: 1,
        maxView: 1
      });
      $(this).datetimepicker("update");
      $(this).on("dp.hide", function(ev) {
        $(this)
          .data("DateTimePicker")
          .show();
        return false;
      });
    });
  },
  propagateSets: function(first, second = undefined, duration = 1) {
    var $setsTable = $(".event-set-list-form .formset_table");
    var $setsTableBody = $(".event-set-list-form .formset_table tbody");
    // Keep first row
    var $firstClone = $setsTable.find("tbody tr:first").clone();

    //Remove original id and ensure is shown
    $firstClone.find('input[id$="id"]').val("");
    $firstClone.show();

    var total = 0;
    $setsTable.find("tbody tr").each(function() {
      var row = $(this);
      var value = row.find('input[id$="id"]').val();
      if (value && value !== "") {
        // Mark sets without id as deleted
        total++;
        row.hide();
        var del = row.find('input[id$="DELETE"]')[0];
        $(del).val(true);
      } else {
        // Remove new entered sets
        row.remove();
      }
    });

    //
    var $total = $("#id_sets-TOTAL_FORMS");
    $total.val(total);

    var firstRow = EventForm.cloneMore($firstClone, undefined, "sets");
    firstRow.appendTo($setsTableBody);
    this.configureTimePicker(firstRow);
    firstRow
      .find("#id_sets-" + total + "-start")
      .data("DateTimePicker")
      .setDate(first);
    firstRow
      .find("#id_sets-" + total + "-end")
      .data("DateTimePicker")
      .setDate(first.add(duration, "h"));

    if (second) {
      var secondRow = EventForm.cloneMore($firstClone, undefined, "sets");
      secondRow.appendTo($setsTableBody);
      this.configureTimePicker(secondRow);
      secondRow
        .find("#id_sets-" + (total + 1) + "-start")
        .data("DateTimePicker")
        .setDate(second);
      secondRow
        .find("#id_sets-" + (total + 1) + "-end")
        .data("DateTimePicker")
        .setDate(second.add(duration, "h"));
    }

    this.fixTableWidths($setsTable);
  },
  initSetsTimePickers: function() {
    var $setsTable = $(".event-set-list-form .formset_table");
    var $set_row = $setsTable.find("tbody tr:first").clone(true);
    this.configureTimePicker($setsTable);
    $setsTable.find("input.timeinput").each(function() {});

    var addButtonSelector = "#add_more_sets";
    var tableType = "sets";

    this.fixTableWidths($setsTable);

    $(document).on("click", addButtonSelector, function() {
      var $lastRow = $setsTable.find("tbody tr:last");
      var newRow = EventForm.cloneMore($set_row, $lastRow, tableType);
      EventForm.fixTableWidths($setsTable);
      EventForm.configureTimePicker(newRow);
    });

    $(document).on("click", ".artist_remove", function(e) {
      // hide the entry and set the DELETE value to true so Django knows to delete it
      $(this)
        .parents("tr")
        .hide();
      var del = $(this)
        .parents("tr")
        .find('input[id$="DELETE"]')[0];
      $(del).val(true);
      EventForm.fixTableWidths($setsTable);
      return false;
    });
  },
  initInlineArtistsFunctionality: function(callback) {
    var $artistTable = $(".artist-list-form .formset_table");
    var tableType = "artists_gig_info";
    var buttonRemove = $artistTable.find(".artist_remove");

    var $artistRow = $artistTable.find("tbody tr:first").clone(true);
    $artistRow.find(".artist_field option:not(:first)").remove();

    $artistTable.find("select").selectize({
      create: false
    });

    // Dynamically sets the default instrument for an artist
    $(document).on("change", ".artist_field", function(e) {
      var $role_field = $(e.currentTarget)
        .parent()
        .next()
        .find("select");
      var $ajax_role_field = $(e.currentTarget.parentElement).find(
        "select.role_field"
      );
      var value = $(e.currentTarget).val();
      $.get(
        "//" + EventForm.SITE_URL + "/artists/" + value + "/instrument_ajax/",
        function(data) {
          if ($role_field.length > 1) {
            $role_field[0].selectize.setValue(data);
          } else {
            $ajax_role_field[0].selectize.setValue(data);
          }
        }
      );
    });

    $artistTable.find("tbody").sortable({
      // update the sort_order field based on the order in the DOM
      update: function(event, ui) {
        $(".sort_order_field").each(function(index) {
          $(this).val(index);
        });
      }
    });

    this.fixTableWidths($artistTable);

    $(document).on("click", "#add_more_artists", function() {
      var $lastRow = $artistTable.find("tbody tr:last");
      EventForm.cloneMore($artistRow, $lastRow, tableType);
      EventForm.fixTableWidths($artistTable);
    });

    buttonRemove.on("click", function(e) {
      // hide the entry and set the DELETE value to true so Django knows to delete it
      $(this)
        .parents("tr")
        .hide();
      var del = $(this)
        .parents("tr")
        .find('input[id$="DELETE"]')[0];
      $(del).val(true);
      EventForm.fixTableWidths($artistTable);
      return false;
    });

    if (callback) {
      callback();
    }

    //$("#id_title").focus(function() {
    //    if(! $(this).val()) {
    //        var title = $(".artist_field div.item").first().text().trim();
    //        var remaining_artists = $(".artist_field div.item").not(":first");
    //        if (remaining_artists.length > 0) {
    //            title += " w/ ";
    //            remaining_artists.not(':last').each(function() {
    //                title += $(this).text() + ", ";
    //            });
    //            title += remaining_artists.last().text();
    //        }
    //        $(this).val(title);
    //    }
    //});
  },
  initVenueSelectFunctionality: function() {
    $("#div_id_venue select").selectize({
      create: false,
      onChange: function(value) {
        venue = $(
          "#div_id_venue .selectize-dropdown-content [data-value~=" +
            value +
            "]"
        ).text();
        $(".btn.btn-success.slot").hide();
        $(".btn.btn-success.slot[data-venue~=" + venue + "]").show();
      }
    });
  },
  init: function(datepicker, callback) {
    if (datepicker) {
      this.initDateTimeFunctionality();
      this.initSetsTimePickers();
      $("#id_start").datetimepicker("update");
      $("#id_end").datetimepicker("update");
    }
    this.initVenueSelectFunctionality();
    this.initInlineArtistsFunctionality(callback);

    $(document).on(
      "change",
      "#id_sets-0-start, #id_sets-1-start, #id_sets-2-start, #id_sets-3-start",
      function(e) {
        let set = parseInt(this.id[8]) + 1;
        $(`#id_set${set}-set_name`).val($(this).val());
      }
    );
  }
};
