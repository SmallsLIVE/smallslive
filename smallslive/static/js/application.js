$(document).ready(function(){
  //Customer Signup process
  //Trial signup
  $('.f-trial-signup').submit(function(e){
    //AJAX 
    e.preventDefault();
    var email=$(this).find('input[name=subscriber_email]').val();
    //validate email address
    if (email=='') { 
      var emailContainer=$(this).find('input[name=subscriber_email]').closest('.form-group');
      emailContainer.addClass('has-error has-feedback').append('<span class="glyphicon glyphicon-remove form-control-feedback"></span>');
    } else {
      $('.has-error').removeClass('has-error has-feedback').find('.form-control-feedback').remove();
      $(this).html('<div class="alert alert-success"><p><strong>'+email+'</strong> has been emailed a special link. Click that link to begin your trial. </p><p><a href="#" class="send-verification-link">Resend the link</a> if you haven\'t received your email. </p></div>');
      //Now create a way to resend the verification link or take further action
      $('.f-trial-signup').delegate('a.send-verification-link','click',function(e){
        e.preventDefault();
        //do ajax
        //Give a link to resend verification:
        $(this).closest('p').html('(Sending...)').fadeOut(100).fadeIn(500,function() {
          $(this).replaceWith('<p>Link sent again. If you still haven\'t received the verification link, you can <a href="/static_page/trial-signup">try a new email</a>,  <a href="#">contact us</a>, or <a href="/">return to the homepage.</a>');
        });
      });
    }
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
      $(this).html('<div class="alert alert-success"><p><strong>'+email+'</strong> has emailed password reset instructions.</p><p><a href="#" class="send-verification-link">Resend the link</a> if you haven\'t received your email. </p></div>');
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
  //
  // 
  //Performer Signup process
  function toggleSetList(songsInVideoToPublish) {
    if ($(songsInVideoToPublish).hasClass('some')==true) {
      $(songsInVideoToPublish).closest('tr').find('.set-list').slideDown();
    } else {
      
      $(songsInVideoToPublish).closest('tr').find('.set-list').slideUp();
    }
  }
  $('table.videos-to-publish tr .toggle-all-or-some input').click(function() {
    toggleSetList(this);
    countSelectedVideos();
  });  
  $('table.videos-to-publish tr .toggle-all-or-some input').each(function(i) {
    toggleSetList(this);
    countSelectedVideos();
  });  
  //Init
  $('table.videos-to-publish tr .set-list').hide(); 
  //  Count selected videos. If none selected for publishing, show a warning.
  function countSelectedVideos() {
    var cnt, div;
    div=$('div.alert-info');
    div.show();
    cnt=$('table.videos-to-publish tbody tr').length;
    cntTotallyUnpublished=$('table.videos-to-publish input.none:checked').length;
    $('.musician-registration .alert-danger').remove();
    //BROKEN - this UI doesnt work right if select-all is clicked. Select-all clicks may report "0" checked
    // because the function that handles selecting-all
    // has not fired yet. As a result, the checkboxes in the group are not checked at the time the CNT
    // is evaluated below:
    if (cntTotallyUnpublished == cnt) { 
      div.hide();
      $('<div class="alert alert-danger">(0) videos were selected. This means none of the videos here can earn revenue on SmallsLIVE for anyone including you. While you can change your mind later, for now, the videos will not appear on SmallsLIVE.</div>').insertAfter(div);
    }
  }
  //Select-all-videos to clear
  //  Init
  if ($('table.videos-to-publish').length > 0) {
    countSelectedVideos();
  }
  //End signup
  
  //ADMIN forms begin
  function checkRadio(radio) {
    if ($(radio).hasClass('extra-message')==true) {
      $('.trigger-add-extra-message').next('div').slideDown();
    } else {
      
      $('.trigger-add-extra-message').next('div').slideUp();
    }
  }
  //Let me add a welcome message when inviting artists
  $('.f-add-artist').delegate('input[name=invitation]','change',function(){
    checkRadio(this);
  });
  //Init
  if ($('.f-add-artist').length > 0) {
    checkRadio('input[name=invitation]');
  }
  //Date fields need a picker
  $('#id_start_day').datepicker().on('changeDate', function(ev){
    $('#id_start_day').datepicker('hide');
    //loading state during query - probably show spinner
    $('.f-gig .slot input').prop('disabled',true);
    $('.f-gig .slot input[type=text]').val('Checking availability..');
    
    //TODO: AJAX
    //callback function: populate the slots properly:
    //unhide the checkboxes, undisable fields, fill in labels and input slots appropriately:
    
  });;
  
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

});