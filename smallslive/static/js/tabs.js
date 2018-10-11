(function($) {
  /* Tabs.js
    Tab: Put data-toggle-tab-target="name" in any clickable element.
    Tab content: Put data-toggle-tab="name" in any other element.
    
    Optional:
    Tab Group: Put data-toggle-tab-group="groupname" in both elements.
    
    Clicking the element will:
      * Hide any siblings of the Tab Content (with the data attribute) unless tab-group is used,
         in which case they are matched my group name instead of siblinhood.
      * Add 'active' class to the tab and remove it from its siblings (with the data atribute).
  **/
  $(document).on('click', '[data-toggle-tab-target]', function() {
    $(this).siblings('[data-toggle-tab-target]').removeClass('active');
    $(this).addClass('active');
    
    var tabName = $(this).data('toggle-tab-target');
    var tabGroup = $(this).data('toggle-tab-group');
    var $target = $('[data-toggle-tab="' + tabName + '"]');

    if (tabGroup) {
      $('[data-toggle-tab-group="' + tabGroup + '"][data-toggle-tab]').hide();
    } else {
      $target.siblings('[data-toggle-tab]').hide();
    }
    $target.show();
  });
})(window.jQuery);
