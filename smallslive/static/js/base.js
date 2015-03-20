/* Solves issues with images filling div's. Adds a img.wide or img.tall class to img element. */

/*!
 * $.fn.scrollIntoView - similar to the default browser scrollIntoView
 * The default browser behavior always places the element at the top or bottom of its container.
 * This override is smart enough to not scroll if the element is already visible.
 *
 * Copyright 2011 Arwid Bancewicz
 * Licensed under the MIT license
 * http://www.opensource.org/licenses/mit-license.php
 *
 * @date 8 Jan 2013
 * @author Arwid Bancewicz http://arwid.ca
 * @version 0.3
 */
(function(a){a.fn.scrollIntoView=function(f,j,c){var b=a.extend({},a.fn.scrollIntoView.defaults);if(a.type(f)=="object"){a.extend(b,f)}else{if(a.type(f)=="number"){a.extend(b,{duration:f,easing:j,complete:c})}else{if(f==false){b.smooth=false}}}var h=Infinity,e=0;if(this.size()==1){((h=this.get(0).offsetTop)==null||(e=h+this.get(0).offsetHeight))}else{this.each(function(m,n){(n.offsetTop<h?h=n.offsetTop:n.offsetTop+n.offsetHeight>e?e=n.offsetTop+n.offsetHeight:null)})}e-=h;var k=this.commonAncestor().get(0);var g=a(window).height();while(k){var d=k.scrollTop,l=k.clientHeight;if(l>g){l=g}if(l==0&&k.tagName=="BODY"){l=g}if((k.scrollTop!=((k.scrollTop+=1)==null||k.scrollTop)&&(k.scrollTop-=1)!=null)||(k.scrollTop!=((k.scrollTop-=1)==null||k.scrollTop)&&(k.scrollTop+=1)!=null)){if(h<=d){i(k,h)}else{if((h+e)>(d+l)){i(k,h+e-l)}else{i(k,undefined)}}return}k=k.parentNode}function i(n,m){if(m===undefined){if(a.isFunction(b.complete)){b.complete.call(n)}}else{if(b.smooth){a(n).stop().animate({scrollTop:m},b)}else{n.scrollTop=m;if(a.isFunction(b.complete)){b.complete.call(n)}}}}return this};a.fn.scrollIntoView.defaults={smooth:true,duration:null,easing:a.easing&&a.easing.easeOutExpo?"easeOutExpo":null,complete:a.noop(),step:null,specialEasing:{}};a.fn.isOutOfView=function(b){var c=true;this.each(function(){var h=this.parentNode,d=h.scrollTop,g=h.clientHeight,f=this.offsetTop,e=this.offsetHeight;if(b?(f)>(d+g):(f+e)>(d+g)){}else{if(b?(f+e)<d:f<d){}else{c=false}}});return c};a.fn.commonAncestor=function(){var c=[];var f=Infinity;a(this).each(function(){var g=a(this).parents();c.push(g);f=Math.min(f,g.length)});for(var d=0;d<c.length;d++){c[d]=c[d].slice(c[d].length-f)}for(var d=0;d<c[0].length;d++){var e=true;for(var b in c){if(c[b][d]!=c[0][d]){e=false;break}}if(e){return a(c[0][d])}}return a([])}})(jQuery);

function makeImagesResponsive(selector) {
    $(selector).find('img').each(function () {
        var imgClass = (this.width / this.height > 1) ? 'wide' : 'tall';
        $(this).addClass(imgClass);
    });
}

$(window).load(function () {
    makeImagesResponsive('.container');
});

$(function() {
    // setTimeout() function will be fired after page is loaded
    // it will wait for 5 sec. and then will fire
    // $("#successMessage").hide() function
    setTimeout(function() {
        $(".alert-dismissible").hide(500);
    }, 10000);
});

/* Adds swipe ability to Bootstrap event carousel */
$(document).ready(function () {
    $carousel = $("#upcoming-carousel");
    $carousel.swiperight(function () {
        $(this).carousel('prev');
    });
    $carousel.swipeleft(function () {
        $(this).carousel('next');
    });
});


/* Initialize Slick responsive carousel for Archive page */
$(document).ready(function () {
    $('.archive-carousel').slick({
        dots: true,
        slidesToShow: 4,
        slidesToScroll: 4,
        responsive: [
            {
                breakpoint: 992,
                settings: {
                    slidesToShow: 3,
                    slidesToScroll: 3
                }
            },
            {
                breakpoint: 767,
                settings: {
                    slidesToShow: 2,
                    slidesToScroll: 2
                }
            }
        ]
    });
});


/* Expanding details for schedule */
$(document).ready(function () {
    var active = 0;
    $(".day").click(function () {
        var position = $(this).data('position');
        $("#event-details-expanded").remove();
        $(".selected").removeClass('selected');
        if (position !== active) {
            var that = this;
            var date = $(this).attr('data-date');

            $.get('/events/event_carousel_ajax/?date=' + date, function (data) {
                var template = data.content;

                $(that).addClass('selected');
                /* larger devices */
                var offset;
                if ($(window).width() > 768) {
                    offset = (4 - (position % 4)) % 4;
                }
                /* smaller devices */
                else {
                    offset = position % 2;
                }
                var new_position = position + offset;
                $('div[data-position=' + new_position + ']').after(template);

                active = position;
                makeImagesResponsive(".container");
                $("#event-details-expanded").scrollIntoView();
            });
        } else {
            active = 0;
        }
    });
});


/* Event data for the homepage */
$(document).ready(function () {
    var active = 0;
    $("body").on('change', '#homepage-date-select', function (d) {
        var date = $(this).val();
        var $carousel =
        $.get('/events/event_carousel_ajax/?template=home&date=' + date, function (data) {
                var template = data.content;
                $("#upcoming-events-fullsize").replaceWith(template);
                makeImagesResponsive('#upcoming-events-fullsize');
            });
    });
});


/* Header search autocomplete */

$.widget( "custom.catcomplete", $.ui.autocomplete, {
    _create: function() {
      this._super();
      this.widget().menu( "option", "items", "> :not(.ui-autocomplete-category)" );
    },
    _renderMenu: function( ul, items ) {
        var that = this,
        currentCategory = "";
        console.log(items);

        $.each ( items[1], function( index, item ) {
            var li;
            if ( item.category != currentCategory ) {
                if ( currentCategory != "" && items[0][currentCategory] > 5 ) {
                    ul.append ( "<li class='ui-autocomplete-more-count'><a href='/search/" + currentCategory + "/?q=" + that.term + "'>+" + ( items[0][currentCategory] - 5 ) + " more</a></li>" );
                }
                currentCategory = item.category;
                ul.append ( "<li class='ui-autocomplete-category'><span class='name'>" + item.category + "</span><span class='results-count'>(" + items[0][currentCategory] + ")</span></li>" );
            }
            li = that._renderItemData( ul, item );
            if ( item.category ) {
              li.attr( "aria-label", item.category + " : " + item.label );
            }
        });
        if ( currentCategory != "" && items[0][currentCategory] > 5 ) {
                    ul.append ( "<li class='ui-autocomplete-more-count'><a href='/search/" + currentCategory + "/?q=" + that.term + "'>+" + ( items[0][currentCategory] - 5 ) + " more</a></li>" );
                }
    },
    _renderItem: function( ul, item ) {
        return $( "<li>" )
            .attr( "data-value", item.value )
            .append('<a href="' + item.url + '"><span class="name">' + item.label + '</span><span class="sublabel">' + item.sublabel + "</span></a>" )
            .appendTo( ul );
    }
  });

$(function() {
    $( ".search__input" ).catcomplete({
      delay: 500,
      source: '/search/autocomplete/',
      minLength: 3,
      appendTo: '#header-search-container'
    });
  });

/* Header search focus effect */
$(document).ready(function () {
    $('.search__input').on('blur', function(){
        $('.navigation__item').removeClass('search-active');
    }).on('focus', function(){
        $('.navigation__item').addClass('search-active');
    });
});
