$(document).ready(function(){
  //If customer opts in to pay for subscription during signup of trial,
  //  show credit card fields on signup page:
  $('#signup_form .credit-card-fields').hide();
  function setSignupPaymentType(upgradeNowCheckbox) {
    if ($(upgradeNowCheckbox).is(":checked")) {
      $('.credit-card-fields').slideDown();
    } else {
      $('.credit-card-fields').slideUp();
    }
  }
  $('.trigger-credit-card-fields input').on('change',function(){
    setSignupPaymentType(this);
  });
  //init - case webpage caches checkmark status, we need to reset the UI:
  setSignupPaymentType($('.trigger-credit-card-fields input'));
  //When user clicks on sign-up-to-mailing-list checkbox during trial sign-up
  // we want to unmute the text
  function toggleEmailSignupCheckboxLabel(checkbox) {
    if (checkbox.is(':checked')) {
      checkbox.closest('label').removeClass('text-muted');
    } else {
      checkbox.closest('label').addClass('text-muted');
    }
  }
  //Process trial sign up form
  $('#signup_form').submit(function(e){
    //AJAX 
    e.preventDefault();
    //FILL IN ERROR HANDLING
  });
  //Reset password during artist signup
  // This is very similar to Trial signup above and you may want to refactor
  $('.f-reset-password').submit(function(e){
    //AJAX 
    e.preventDefault();
    var email=$(this).find('input[name=artist_email]').val();
    //validate email address
    if (email=='') { 
      var emailContainer=$(this).find('input[name=artist_email]').closest('.form-group');
      emailContainer.addClass('has-error has-feedback').append('<span class="glyphicon glyphicon-remove form-control-feedback"></span>');
    } else {
      $('.has-error').removeClass('has-error has-feedback').find('.form-control-feedback').remove();
      $(this).html('<div class="alert alert-success"><p><strong>'+email+'</strong> has been emailed password reset instructions.</p><p><a href="#" class="send-verification-link">Resend the link</a> if you haven\'t received your email. </p><p>Remembered your password? <a href="/static_page/musician-signup-login/">Log in to continue artist registration</a></p></div>');
      //Now create a way to resend the verification link or take further action
      $('.f-reset-password').delegate('a.send-verification-link','click',function(e){
        e.preventDefault();
        //do ajax
        //Give a link to resend verification:
        $(this).closest('div.alert-success').html('(Sending...)').fadeOut(100).fadeIn(500,function() {
          $(this).replaceWith('<div class="alert alert-success">Link sent again. If you still haven\'t received the verification link, you can <a href="/static_page/musician-signup-rescue-password">try a different email address</a>,  <a href="#">email artistHelp@smallslive.com</a>, or <a href="/">return to the homepage.</a></div>');
        });
      });
    }
  }); 
  //END CUSTOMER SIGN UP FORMS


  //When i approve or disapprove a master, make my name green or red
  $('.f-toggle-publish').on('submit',function(){
    $(this).replaceWith('<p class="text-success clearance-summary"><span class="glyphicon glyphicon-ok"></span> This video is now published. <a href="#"  class="trigger-show-musician-registration-status">Performer details&hellip;</a></p><p class="text-warning clearance-summary"><span class="glyphicon glyphicon-ok"></span> Video will be published once all performers on it have joined SmallsLIVE. <a href="#" class="trigger-show-musician-registration-status">Performer details&hellip;</a></p>');
 
    return false;
  });   
  //ARTIST SIGNUP:
  // Hide list of recordings until "only publish selected recordings" radio is clicked
  $('.musician-registration .show-recordings').hide();
  function showOrHideListOfRecordings(someOrAll) {
    //alert(someOrAll);
    if (someOrAll=='some') {
      $('.show-recordings').slideDown();
    } else {
      $('.show-recordings').slideUp();
    } 
  }
  $('input[name=trigger-show-recordings]').on('click',function() {
    showOrHideListOfRecordings($(this).val());
  });
  //init - to deal with cached radios
  showOrHideListOfRecordings($('input[name=trigger-show-recordings]:checked').val());
  //Show video player in popup on musician-signup-choose-videos
  $('#popup-player').dialog({
    autoOpen:false,
    modal:true,
    width: 700
  });
  $('table.list-of-recordings').on('click','.video-thumb a:not(.download), .audio-play a:not(.download)',function(e)     {
    e.preventDefault();
    var mediaRow=$(this).closest('tr');
    var mediaDate=mediaRow.find('.event_date').text();
    var mediaDescription=mediaRow.find('.description').html();
    $('#popup-player').dialog('option','title',mediaDate);
    $('#popup-player').dialog('open');
    $('#popup-player .description').html(mediaDescription);
  });
  //end show video in popup  
  //On artist/edit, let artist set payment-distribution-method:
  function showCorrectPaymentFields(DDorCheck) {
    if (DDorCheck=='DD') {
      $('.payment-via-check').hide();
      $('.payment-via-DD').show();
    } else {
      $('.payment-via-DD').hide();
      $('.payment-via-check').show();
    }
  }
  //INIT - handle cached radios:
  showCorrectPaymentFields($('form input[name=payment-distribution-method]:checked').val());
  $('form').on('click','input[name=payment-distribution-method]',function() {
    showCorrectPaymentFields($(this).val());
  });
  //END payment-distribution-method
  //END ARTIST SIGNUP
  
  
  //SUPER ADMIN forms:
  $('.artist-clearance-breakdown table').hide();
  $('body').on('click','.clearance-summary a.trigger-show-musician-registration-status',function(e){
    e.preventDefault();
    $(this).closest('.artist-clearance-breakdown').find('table').toggle();
  });
  function checkRadio(radio) {
    if ($(radio).filter(':checked').hasClass('custom_invite')) {
      $('.extra-message').slideDown();
    } else {
      $('.extra-message').slideUp();
    }
  }
  //Let me add a welcome message when inviting artists
  $('.f-add-artist').delegate('input[name=invite_type]','change',function(){
    checkRadio(this);
  });
  //Init
  if ($('.f-add-artist').length > 0) {
    checkRadio('input[name=invite_type]');
  }
  //Date fields need a picker
  $('#id_date').datepicker().on('changeDate', function(ev){
    $('#id_date').datepicker('hide');
    //loading state during query - probably show spinner
    $('.f-gig .slot input').prop('disabled',true);
    $('.f-gig .slot input[type=text]').val('Checking availability..');
    
    //TODO: AJAX
    //callback function: populate the slots properly:
    //unhide the checkboxes, undisable fields, fill in labels and input slots appropriately:
    
  });
  //Draggable musician ordering
  $('.f-gig div.sortable-list').sortable({
    //AJAX in here
    //For accessibility, we probably should use a method where we pass a value 
    //  to a hidden text input (not hidden) input field such that there is a keyboard
    //  accessible method to enter the position.
    
  });
  //Muting
  //Make checkbox+textinput fields appear selected or muted. By default, we assume
  // .text-muted was assigned to the text input
  $('.input-group-addon input').on('change',function(){
    setupInputGroupAddOns($(this));
  });
  function setupInputGroupAddOns(o) {
    var textinput=o.closest('.form-group').find('input[type=text]');
    textinput.removeClass('text-muted');
    if (o.is(':checked')==false) {
      textinput.addClass('text-muted');
    }
  }
  //init
  $('.input-group-addon input').each(function(i){
    setupInputGroupAddOns($(this));
  });
  //Make rarely used fields become unmuted on focus or blur w/ content
  $('form').delegate('#id_title, #id_subtitle','focus',function() {
    var label=$(this).closest('.form-group').find('label');
    label.removeClass('text-muted');
    $(this).on('blur',function() {
      if ($(this).val()=='') {
        label.addClass('text-muted');
      } 
    });
  });
  //Make autocompleters for name , genre, instruments
  $('.sideman_name').each(function(i){
    $(this).selectize({
      create: true,
      sortField: 'text',
      maxItems:1
    })
  });
  $('.sideman_instruments, input[name=genres], input[name=instruments]').each(function(i){
    $(this).selectize({
      delimiter: ',',
      persist: false,
      create: function(input) {
          return {
              value: input,
              text: input
          }
      }
    })
  });
  //Allow set times to be entered
  function toggle_add_set_times(checkbox,fields) {
    var fields=$(checkbox).closest('.row').next('.add_set_times');
    if ($(checkbox).is(':checked')==true) {
      fields.slideDown();
    } else {
      fields.slideUp();
    }
  }
  $('.trigger_add_set_times input').change(function() {
    toggle_add_set_times(this);
  }); 
  //init
  $('.trigger_add_set_times input').each(function(i) {
    toggle_add_set_times(this);
  }); 
  //END ADMIN FORMS
  
  //MY ACCOUNT STUFF
  //View orders -toggle order search form UIs
  $('a.trigger-search-orders-by-date').on('click',function(e) {
    e.preventDefault();
    $(this).closest('.row').hide();
    $('.row.search-orders-by-date').show();
  });
  $('a.trigger-search-orders-by-number').on('click',function(e) {
    e.preventDefault();
    $(this).closest('.row').hide();
    $('.row.search-orders-by-number').show();
  });
  //Mailing list signup from my-account page
  $('a.trigger-subscribe').on('click',function(e) {
    e.preventDefault();
    var container=$(this).closest('td');
    $(this).closest('div').fadeOut(500,function() {
      container.find('.alert').remove();
      container.prepend('<p class="alert alert-success">You are now on the SmallsLIVE mailing list.</p>');
      $('div.mailinglist-joined').fadeIn();
    });
  });
  $('a.trigger-unsubscribe').on('click',function(e) {
    e.preventDefault();
    var container=$(this).closest('td');
    $(this).closest('div').fadeOut(500,function() {
      container.find('.alert').remove();
      container.prepend('<p class="alert alert-success">You have been unsubscribed from our list.</p>');
    });
    $('div.mailinglist-not-joined').fadeIn();
  });
  //END MY ACCOUNT 
  // MY GIGS
  $('.bulk-download .download-configurator').hide();
  $('.bulk-download').on('click','.trigger-for-content a',function(e) {
    e.preventDefault();
    var container=$('.bulk-download');
    container.find('.download-configurator').toggle();
  });
  //When I change sets in the table with radio button, highlight the proper radio button
  $('.choose-set').on('click','input',function(){
    var id=$(this).closest('tr').data("event");
    var row=$('tr.event_'+id+' .choose-set');
    row.find('label span').removeClass('glyphicon glyphicon-arrow-right');
    
    row.removeClass('active');
    $(this).closest('.choose-set').addClass('active');
    $(this).closest('label').find('span').addClass('glyphicon glyphicon-arrow-right');
  });
  //END MY GIGS
  //BEGIN ARTIST $ DASHBOARD
  //Toggle display of each store items $ earnings over different time periods (each item has 4 hidden
  //  rows of breakdown data that is hidden by default until the product title is clicked
  $('table.store-revenue-per-item-breakdown table, table.store-revenue-per-item-breakdown tr.item-earning-detail-over-time-period').hide();
  $('table.store-revenue-per-item-breakdown').on('click','.product > a:first-child',function(e) {
    e.preventDefault();
    var productRow=$(this).closest('tr');
    var product_id=productRow.attr('product_id');
    console.log('x: '+$('tr.belongs_to_'+product_id+':first-child').css('display'));
    if (productRow.next('tr').css('display')!='table-row') {
      $(this).find('span').removeClass('glyphicon-expand').addClass('glyphicon-collapse-down');
      $(productRow).find('td:first-child').attr('rowspan','5');
      $('tr.belongs_to_'+product_id).show();
      productRow.children('td').css('font-weight','bold');
    } else {
      $(this).find('span').removeClass('glyphicon-collapse-down').addClass('glyphicon-expand');
      $(productRow).find('td:first-child').attr('rowspan','1');
      $('tr.belongs_to_'+product_id).hide();
      productRow.children('td').css('font-weight','normal');
    }
  });
  //END ARTIST $ DASHBOARD 
  
  
  //PUBLIC PAGES
  //EVENT PAGE/VIDEO PAGE
  //Change publish flag:
  //First, the fake form should show an "are you sure mesg:"
  $('.f-publish-video').on('click','.default a.trigger-unpublish',function(e) {
    e.preventDefault();
    $('.f-publish-video .default').hide();
    $('.f-publish-video .are-you-sure').show();
  });
  //Now that the ARE YOU SURE UI is showing, process form, or cancel :
  $('.f-publish-video').on('click','.are-you-sure .btn',function() {
    if ($(this).val()=='Leave Published') {
      //Dont save form; return UI to default state:
      $('.f-publish-video .are-you-sure').hide();
      $('.f-publish-video .default').show();
      return false; 
    } else {
      //Process Unpublish action:
      return true;
    }
  });
  //END Change Publishing Status
  
  //EVENT PAGE - 
  //AUDIO PLAYER:
 
  $('.event').on('click','a.sm2_button',function(e) {
    e.preventDefault();
    $('a.sm2_button').find('span.glyphicon-pause').removeClass('glyphicon-pause').addClass('glyphicon-play');   
    if ($(this).hasClass('sm2_playing')!=true) {
      console.log('playing');
      $(this).find('span.glyphicon-play').removeClass('glyphicon-play').addClass('glyphicon-pause');    
    }
  });
 
  //Show event description when present:
  $('.event').on('click','.trigger-show-event-description',function(e) {
    e.preventDefault();
    $(this).closest('.event-meta').find('.description').toggle();
  });
  //Favorite a video:
  $('.event').on('click','.trigger-favorite-video',function(e) {
    e.preventDefault();
    if ($(this).hasClass('btn-primary')) {
      $(this).removeClass('btn-primary').addClass('btn-success');
      $(this).html('<span class="glyphicon glyphicon-ok"></span> Favorited');
    } else {
      $(this).removeClass('btn-success').addClass('btn-primary');
      $(this).html('<span class="glyphicon glyphicon-star"></span> Favorite');
    }
  });
  //Request a missing video be expedited on video.html
  $('.request-video').on('click','a.trigger-request-video',function(e) {
    e.preventDefault();
    var newcount;
    var countHolder=$('.request-video .request-count');
    var requestCount=parseInt(countHolder.text());
    if ($(this).hasClass('btn-primary')) {
      $(this).removeClass('btn-primary').addClass('btn-success');
      $(this).html('<span class="glyphicon glyphicon-ok"></span> Requested');
      newCount=requestCount+1;
      countHolder.text(newCount);
    } else {
      $(this).removeClass('btn-success').addClass('btn-primary');
      $(this).html('<span class="glyphicon glyphicon-star"></span> I want it ASAP!');
      newCount=requestCount-1;
      countHolder.text(newCount);
    }
  });
  //CONTACT ARTIST BY FAN - POPUP WINOW TO SEND EMAIL
  $('#send-message').dialog({
    autoOpen:false,
    modal:true,
    width: 500
  });
  $('#send-message').on('submit','form',function() {
    $('#send-message').on('click',' .btn-success',function() {
      $('#send-message').dialog('close');
      //remove feedback message and re-show the form (which is hidden since dialog is closed)
      $('#send-message .message-sent-feedback').remove();
      $('#send-message form').show();
    });
    $(this).hide().after('<p class="message-sent-feedback text-success"><span class="glyphicon glyphicon-ok"></span> Message sent. <code>3</code> </p><button  class="btn btn-sm btn-success">Ok</button></div>');
    return false;
  });
  $('.trigger-send-message').click(function(e)     {
    e.preventDefault();
    $('#send-message').dialog('open');
  });  
  //END CONTACT ARTIST
  //Request to join artist mailing list on artist_detail.html
  $('.join-artist-mailing-list').on('submit','form',function() {
    $(this).closest('div').find('.alert').remove();
    $(this).before('<div class="alert-success alert">Request sent to artist. This is not an automated process so you may want to follow up later to make sure they received your request.</div>');
    $(this).hide();
    return false;
  });
  $('.join-artist-mailing-list .alert').on('click','a',function(e) {
    e.preventDefault();
    $('.join-artist-mailing-list .alert').remove();
    $('.join-artist-mailing-list form').slideDown();
  });
  //...or show the form even if they have and want to request again

  

});