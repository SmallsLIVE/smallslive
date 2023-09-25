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

    /* Currently mobile and desktop have different tabs. In order to
    keep them synced, we need to modify both tabs active state */

    var siblings = $(this).siblings('[data-toggle-tab-target]');
    siblings.each(function () {
      var value = $(this).attr('data-toggle-tab-target');
      $('[data-toggle-tab-target="' + value + '"]').removeClass('active');
    });

    $(this).addClass('active');
    var value = $(this).attr('data-toggle-tab-target');
    $('[data-toggle-tab-target="' + value + '"]').addClass('active');

    var tabName = $(this).data('toggle-tab-target');
    var tabGroup = $(this).data('toggle-tab-group');
    var $target = $('[data-toggle-tab="' + tabName + '"]');

    if (tabGroup) {
      if ($(this).data("toggle-hide") === "no") {
        $('[data-toggle-tab-group="' + tabGroup + '"][data-toggle-tab]').removeClass("active");
      } else {
        $('[data-toggle-tab-group="' + tabGroup + '"][data-toggle-tab]').hide();
      }
    } else {
      if ($(this).data("toggle-hide") === "no") {
        $target.siblings('[data-toggle-tab]').removeClass("active");
      } else {
        $target.siblings('[data-toggle-tab]').hide();
      }
    }
    if ($(this).data("toggle-hide") === "no") {
      if (!$target.hasClass("active")) {
        $target.addClass("active");
      }
    } else {
      $target.show();
    }
  });




})(window.jQuery);
