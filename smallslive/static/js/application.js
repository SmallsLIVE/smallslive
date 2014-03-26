$(document).ready(function(){
  //Public website
  //  Signup process
  function countSelectedVideos() {
    var cnt='';
    cnt=$('tr td.videos input:not(.select-all):checked').length;
    if ($('tr td.videos input:not(.select-all):checked').length > 0) {
      $('.count-videos-to-be-cleared').html(cnt);
    }
  }
  $('table.videos-to-clear').delegate('tr td.videos input.select-all','change',function(i){
    if ($(this).is(':checked')) {
      $(this).closest('td').find('input[type=checkbox]').each(function(i) {
        $(this).prop('checked',true);
      });
    } else {
      $(this).closest('td').find('input[type=checkbox]').each(function(i) {
        $(this).prop('checked',false);
      });
    }
  });
  $('table.videos-to-clear').delegate('tr td.videos input[type=checkbox]','change',function(i){
    countSelectedVideos();
  });
  //Init
  countSelectedVideos();
  
  //  End signup
  //Admin
  //Selectize:
  //Leader - also allow clone of previous gigs:
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