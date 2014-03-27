$(document).ready(function(){
  //Signup process
  //  Count selected videos. If none, show a warning.
  function countSelectedVideos() {
    var cnt, div;
    div=$('.count-videos-to-be-cleared').closest('div.alert-info');
    cnt=$('tr td.videos input:not(.select-all):checked').length;
    $('.alert-danger').remove();
    //BROKEN - this UI doesnt work right if select-all is clicked. Select-all clicks may report "0" checked
    // because the function that handles selecting-all
    // has not fired yet. As a result, the checkboxes in the group are not checked at the time the CNT
    // is evaluated below:
    if (cnt > 0) {
      $('.count-videos-to-be-cleared').html(cnt);
      div.show();
    } else { 
      div.hide();
      $('<div class="alert alert-danger">(0) videos were selected. This means none of the videos here can earn revenue on SmallsLIVE for anyone including you. While you can change your mind later, for now, the videos will not appear on SmallsLIVE.</div>').insertAfter(div);
    }
  }
  //Select-all-videos to clear
  function selectAllVideosInGroup(checkbox) {
    var numOfVideosInGroup=$(checkbox).closest('td').find('input[type=checkbox]:not(.select-all)').length;
    var numOfVideosInGroupCheckedNow=$(checkbox).closest('td').find('input[type=checkbox]:not(.select-all):checked').length;
    if ($(checkbox).is(':checked')) {
      //if it is a select-all checkbox, then toggle the others
      if ($(checkbox).hasClass('select-all') || numOfVideosInGroup==numOfVideosInGroupCheckedNow ) {
        $(checkbox).closest('td').find('input[type=checkbox]').each(function(i) {
          $(this).prop('checked',true);
        });
      }
    } else {
      $(checkbox).closest('td').find('input[type=checkbox].select-all').prop('checked',false);
      //if it is a select-all checkbox, then toggle the others
      if ($(checkbox).hasClass('select-all') || numOfVideosInGroupCheckedNow==0 ) {
        $(checkbox).closest('td').find('input[type=checkbox]').each(function(i) {
          $(this).prop('checked',false);
        });
      }
    } 
    //Now that we're done, count the selected videos and decide if we need to show a message:
    countSelectedVideos();   
  }
  //When a checkbox video in a group of videos is clicked, run this:
  $('table.videos-to-clear').delegate('tr td.videos input[type=checkbox]','change',function(i){
    selectAllVideosInGroup(this);
  });
  //  Init
  countSelectedVideos();
  //End signup
  
  //ADMIN forms begin
  //Date fields need a picker
  $('input[type=date]').datepicker();
  
  //Draggable musician ordering
  $('.f-gig div.sortable-list').sortable({
    //AJAX in here
    //For accessibility, we probably should use a method where we pass a value 
    //  to a hidden text input (not hidden) input field such that there is a keyboard
    //  accessible method to enter the position.
    
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
  $('.sideman_instruments, input[name=genres]').each(function(i){
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
  function toggle_add_set_times() {
    if ($('.trigger_add_set_times').is(':checked')==true) {
      $('.add_set_times').slideDown();
    } else {
      $('.add_set_times').slideUp();
    }
  }
  $('.trigger_add_set_times').change(function() {
    toggle_add_set_times();
  }); 
  
  //init
  toggle_add_set_times();  

});