(function() {
  $(document).on('click', '.close-button', function() {
    $(this).closest('.modal').hide();
  });
}());