VenueForm = {
  SITE_URL: "",
  selectedDate: "",
  fixTableWidths: function(table) {
    table.find("td").each(function() {
      $(this).css("width", $(this).width() + "px");
    });
  },
  cloneMore: function(source, destination, type) {
    var newElement = source.clone();
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
  initSetsTimePickers: function() {
    var $setsTable = $(".event-set-list-form .formset_table");
    var $set_row = $setsTable.find("tbody tr:first").clone(true);
    this.configureTimePicker($setsTable);
    $setsTable.find("input.timeinput").each(function() {});

    var addButtonSelector = "#add_more_sets";
    var tableType = "default_times";

    this.fixTableWidths($setsTable);

    $(document).on("click", addButtonSelector, function() {
      var $lastRow = $setsTable.find("tbody tr:last");
      var newRow = VenueForm.cloneMore($set_row, $lastRow, tableType);
      VenueForm.fixTableWidths($setsTable);
      VenueForm.configureTimePicker(newRow);
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
      VenueForm.fixTableWidths($setsTable);
      return false;
    });
  },
  init: function(datepicker) {
    this.initSetsTimePickers();

    $(document).on(
      "change",
      "#id_default_times-0-start_time, \
      #id_default_times-1-start_time, \
      #id_default_times-2-start_time, \
      #id_default_times-3-start_time",
      function(e) {
        let set = parseInt(this.id[8]) + 1;
        $(`#id_set${set}-set_name`).val($(this).val());
      }
    );
  }
};
