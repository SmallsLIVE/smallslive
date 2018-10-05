(function() {
  /*  - Subpages (a trubute).
    This utility allows using AJAX to retrieve the contents of any view
    and insert it in any DOM element.

    Usage:

    - Add an element with data-supbage-name and data-subpage-url.

    <div data-supbage-name="comments" data-subpage-url="/comments/"></div>

    - Register the subpages in the DOM.
    window.subpages.register();

    - Load the contents.

    - To load all of the subpages.
    window.subpages.loadAll();

    - To reload the one with data-subpage-name="comments"
    var commentsSubpage = window.subpages.get('comments');
    commentsSubpage.load();

     - To change the url of a supbage.
     var commentsSubpage = window.subpages.get('comments');
     commentsSubpage.setUrl('/comments/?page=2');
  **/
  var Subpage = function (name) {
    this.name = name;
    this.element = $('[data-subpage-name="' + name +'"]');
  };

  Subpage.prototype.bindForms = function () {
    this.element.find('form').ajaxForm({
      type: 'post',
      success: function (response) {
        this.element.html(response);
        this.bindForms();
      }.bind(this),
      error: function (response) {
        this.element.html(response);
        this.bindForms();
      }.bind(this)
    });
  };

  Subpage.prototype.load = function () {
    this.element.html('<div class="text1">Loading  ' + this.name + '...</div>');
    $.get(this.element.data('subpage-url'), function (e) {
      this.element.html(e);
      this.bindForms();
    }.bind(this));
  };

  Subpage.prototype.setUrl = function (url) {
    this.element.data('subpage-url', url);
    this.load();
  };

  var SubpageManager = function () {
    this.subpages = {};
  };
  
  SubpageManager.prototype.register = function(subpageName) {
      var $nodes = $('[data-subpage-name]');
      if (subpageName) {
        $nodes = $('[data-subpage-name='+ subpageName +']');
      }
      var manager = this;
      $nodes.each(function () {
        var name = $(this).data('subpage-name');
        manager.subpages[name] = new Subpage(name);
      });
  };
  SubpageManager.prototype.loadAll = function() {
    Object.keys(this.subpages).forEach(function (name) {
      this.subpages[name].load();
    }.bind(this));
  };
  SubpageManager.prototype.get = function(name) {
    return this.subpages[name];
  };

  window.subpages = new SubpageManager();
}());
