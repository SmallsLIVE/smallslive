(function() {
  $(document).on('click', '.close-button', function() {

    var $modal = $(this).closest('.modal');
    $modal.modal('hide');
    // TODO: fix one of the modals not shown correclty
    $modal.hide();
  });
}());