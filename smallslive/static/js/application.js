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
  
  //Selectize:
  //  Leader - also allow clone of previous gigs:
  //  This was copied from the selectize documentation:
  
  $('#id_performers').selectize({
    valueField: 'url',
    labelField: 'name',
    searchField: 'name',
    create: false,
    render: {
        option: function(item, escape) {
            //TODO
            //Return up to 4 recent shows per leader
            return '<div class="selectize-mega-option">' +
                '<h1 class="title">' +
                    '<span class="name">' + escape(item.leadername) + ': </span>' +
                    '<span class="date">clone ' + escape(item.last_performance_date) + ' gig w/</span>' +
                '</h1>' +
                '<span class="description">' + escape(item.sidemen_list_for_date) + '</span>' +
            '</div>';
        }
    },
    score: function(search) {
        var score = this.getScoreFunction(search);
        return function(item) {
            return score(item) * (1 + Math.min(item.watchers / 100, 1));
        };
    },
    load: function(query, callback) {
        if (!query.length) return callback();
        $.ajax({
            //Replace with query to previous concerts
            url: 'https://api.github.com/legacy/repos/search/' + encodeURIComponent(query),
            type: 'GET',
            error: function() {
                callback();
            },
            success: function(res) {
                callback(res.repositories.slice(0, 10));
            }
        });
    } 
  });
  
  //Sidemen:
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
    
$('#select-to').selectize({
    persist: false,
    maxItems: null,
    valueField: 'email',
    labelField: 'name',
    searchField: ['name', 'email'],
    options: [
        {email: 'brian@thirdroute.com', name: 'Brian Reavis'},
        {email: 'nikola@tesla.com', name: 'Nikola Tesla'},
        {email: 'someone@gmail.com'}
    ],
    render: {
        item: function(item, escape) {
            return '<div>' +
                (item.name ? '<span class="name">' + escape(item.name) + '</span>' : '') +
                (item.email ? '<span class="email">' + escape(item.email) + '</span>' : '') +
            '</div>';
        },
        option: function(item, escape) {
            var label = item.name || item.email;
            var caption = item.name ? item.email : null;
            return '<div>' +
                '<span class="label">' + escape(label) + '</span>' +
                (caption ? '<span class="caption">' + escape(caption) + '</span>' : '') +
            '</div>';
        }
    },
    create: function(input) {
        if ((new RegExp('^' + REGEX_EMAIL + '$', 'i')).test(input)) {
            return {email: input};
        }
        var match = input.match(new RegExp('^([^<]*)\<' + REGEX_EMAIL + '\>$', 'i'));
        if (match) {
            return {
                email : match[2],
                name  : $.trim(match[1])
            };
        }
        alert('Invalid email address.');
        return false;
    }
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