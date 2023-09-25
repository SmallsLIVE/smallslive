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



/*  Adds a img.wide or img.tall class to img element. */

function defineImageRatio(element) {
    var imgClass = (element.height / element.width > 1) ? 'tall' : 'wide';
    $(element).addClass(imgClass);
}

$('.defineImageRatio').on('load', function () {
    defineImageRatio(this);
});

/* Initialize Slick responsive carousel */
$(document).ready(function () {
    $('#upcoming-carousel').slick({
        dots: false,
        slidesToShow: 1,
        slidesToScroll: 1,
        arrows: false,
        autoplay: true,
    });

    $(".carousel-indicators").on('click', 'li', function(){
        slideIndex = $(this).attr("data-slickPosition");
        var slider = $( '#upcoming-carousel' );
        slider[0].slick.slickGoTo(slideIndex);
        $(".carousel-indicators li.active").toggleClass( "active" );
        $(this).toggleClass( "active" );
    });

    $('#upcoming-carousel').on('afterChange', this, function(slick, currentSlide){
        var currentSlide = $(this).slick('slickCurrentSlide');
        $(".carousel-indicators li.active").toggleClass( "active" );
        var indicator = $('.carousel-indicators li');
        $(indicator[currentSlide]).toggleClass("active");
    });

    $('#event-view-header').slick({
        dots: false,
        slidesToShow: 1,
        slidesToScroll: 1,
        arrows: false,
        draggable: false,
        swipe: false
    });

    $(".event-view__header__video-link").on('click', function(){
        var slider = $( '#event-view-header' );
        slider[0].slick.slickGoTo(1);
    });

    $(".event-view__header__video__close").on('click', function(){
        var slider = $( '#event-view-header' );
        slider[0].slick.slickGoTo(0);
    });
});


$(function() {
    // setTimeout() function will be fired after page is loaded
    // it will wait for 5 sec. and then will fire
    // $("#successMessage").hide() function
    setTimeout(function() {
        $(".alert-dismissible").hide(500);
    }, 10000);
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


/* Image cover effect emulation function */
function FillDivImg() {
    $('.div-fill-img').each(function() {
        if (this) {
            var img = this;
            imgCoverEffect(img, {
                alignX: 'center',
                alignY: 'middle'
            });
        }
    })
}

$(document).ready(function () {
    FillDivImg();
})


/* Make all carousel slides fill carousel by height */
function CarouselSlideHeight() {
    $(".upcoming-carousel-single").css('height',$("#upcoming-carousel").height());
}

$(document).ready(function () {
    CarouselSlideHeight();
})


/* Square container maker */
$(document).ready(function () {
    $(".square-container").each(function () {
        $(this).height($(this).width());
    })
})

$(window).on('resize', function() {
    $(".square-container").each(function () {
        $(this).height($(this).width());
    })
})

/* CD aspect ratio maker */
$(document).ready(function () {
    $(".cd-ratio-container").each(function () {
        var newheight = $(this).width() / 1.1;
        $(this).height(newheight);
    })
})

$(window).on('resize', function() {
    $(".cd-ratio-container").each(function () {
        var newheight = $(this).width() / 1.1;
        $(this).height(newheight);
    })
})

/* Animated svg graphics for membership pitch */
;jQuery(document).ready(function(){var dN="albums",dS=54,dC="#d21535",dHC="#d21535",dCCOH=false,dET="hover",dA=true,dL=false,dOP=true,mD=200,hD=200,aC="activeicon",aPC="active",dAC="#000000",lDI=JSON.stringify({"albums":{"d":1000,"it":1,"sh":[{"i":{"a":{"p":"M16.742,12H14.6c-0.331,0-0.6,0.269-0.6,0.6v7.523C13.686,20.049,13.353,20,13,20c-1.657,0-3.2,0.895-3.2,2s1.543,2,3.2,2s3-0.895,3-2v-8c1,0,2,2,2,4c0,0,1.188-2.408,0.594-3.699C18,13,17,13,16.742,12z","s":"none","fl":"#333"}},"f":{}},{"i":{"a":{"p":"M26,24L26,24h2.801C29.463,24,30,23.463,30,22.801V5.2C30,4.537,29.463,4,28.801,4H7.2C6.537,4,6,4.537,6,5.2V8l0,0h2V6h20v16h-2V24z","o":1,"t":"","s":"none","fl":"#333"}},"f":{"5":{"p":"M6.302,23.596C6.521,23.844,6.842,24,7.2,24h21.601C29.463,24,30,23.463,30,22.801V5.2C30,4.537,29.463,4,28.801,4H7.2C6.537,4,6,4.537,6,5.2v17.601C6,23.105,6.114,23.385,6.302,23.596L8,22V6h20v16H8L6.302,23.596z"},"33":{"t":"t-4,4"},"50":{},"83":{"o":0,"t":"t-33,31"},"84":{"o":0,"t":"t9,-11","p":"M26,24L26,24h2.801C29.463,24,30,23.463,30,22.801V5.2C30,4.537,29.463,4,28.801,4H7.2C6.537,4,6,4.537,6,5.2V8l0,0h2V6h20v16h-2V24z"},"100":{"o":1,"t":""},"16.5":{}}},{"i":{"a":{"p":"M2.302,27.596C2.521,27.844,2.842,28,3.2,28h21.601C25.463,28,26,27.463,26,26.801V9.2C26,8.537,25.463,8,24.801,8H3.2C2.537,8,2,8.537,2,9.2v17.601C2,27.105,2.114,27.385,2.302,27.596L4,26V10h20v16H4L2.302,27.596z","o":1,"t":"","s":"none","fl":"#333"}},"f":{"33":{"o":0,"t":"t-30,27"},"34":{"t":"t11,-13"},"50":{"o":1,"t":"t4,-4"},"68":{"p":"M2.302,27.596C2.521,27.844,2.842,28,3.2,28h21.601C25.463,28,26,27.463,26,26.801V9.2C26,8.537,25.463,8,24.801,8H3.2C2.537,8,2,8.537,2,9.2v17.601C2,27.105,2.114,27.385,2.302,27.596L4,26V10h20v16H4L2.302,27.596z"},"83":{"t":""},"100":{},"66.5":{}}}]},"users-add":{"d":1200,"it":1,"sh":[{"i":{"a":{"p":"M25,2c-2.762,0-5,2.24-5,5s2.238,5,5,5s5-2.24,5-5S27.762,2,25,2zM28,8h-2v2h-2V8h-2V6h2V4h2v2h2V8z","t":"","s":"none","fl":"#333"}},"f":{"10":{"t":"s1.4"},"15":{},"25":{"t":""},"100":{}}},{"i":{"a":{"p":"M18.379,24.414c-0.988-0.406-1.385-1.533-1.385-1.533s-0.445,0.256-0.445-0.457c0-0.717,0.445,0.457,0.893-2.301c0,0,1.234-0.359,0.988-3.322h-0.295c0,0,0.742-3.17,0-4.241c-0.744-1.073-1.003-1.93-2.678-2.301c-1.537-0.341-1.039-0.31-2.23-0.259c-1.189,0.053-2.183,0.617-2.183,0.974c0,0-0.743,0.052-1.04,0.359C9.706,11.64,9.21,13.069,9.21,13.428c0,0.357,0.333,2.76,0.581,3.271l-0.38,0.102c-0.248,2.963,0.991,3.322,0.991,3.322c0.445,2.758,0.893,1.584,0.893,2.301c0,0.713-0.447,0.457-0.447,0.457s-0.396,1.127-1.387,1.533c-0.991,0.41-6.493,2.604-6.941,3.066C2.071,27.941,2.122,30,2.122,30h23.597c0,0,0.049-2.059-0.396-2.52C24.873,27.018,19.373,24.824,18.379,24.414z","t":"","s":"none","fl":"#333"}},"f":{"0":{"t":"t-29,0"},"30":{},"65":{"t":"","e":">"},"100":{}}},{"i":{"a":{"p":"M28.378,16.92c-0.033-0.321-0.1-0.605-0.226-0.798c-0.57-0.852-0.796-1.417-2.043-1.824c-1.113-0.315-0.796-0.321-1.702-0.282c-0.904,0.042-1.66,0.563-1.66,0.856c0,0-0.564,0.036-0.793,0.281c-0.217,0.227-0.561,1.238-0.598,1.594h0.021l0.063,0.767c0.016,0.193,0.016,0.365,0.026,0.544c0.066,0.563,0.16,1.141,0.254,1.344l-0.221,0.079c-0.188,2.346,0.76,2.629,0.76,2.629c0.336,2.186,0.677,1.252,0.677,1.823c0,0.565,0.089,0.397,0,0.565c4.31,1.955,4.48,2.748,4.465,5.501H30v-3.606c-0.015-0.006-1.655-0.878-1.661-0.882c-0.758-0.325-1.062-1.216-1.062-1.216s-0.34,0.203-0.34-0.362c0-0.571,0.34,0.362,0.684-1.823c0,0,0.629-0.191,0.754-1.549v-1.037c0-0.013,0-0.027-0.001-0.043h-0.223c0,0,0.164-0.75,0.224-1.571v-0.99H28.378z","t":"","s":"none","fl":"#333"}},"f":{"0":{"t":"t14,0"},"30":{},"65":{"t":"","e":">"},"100":{}}}]},"heart":{"d":300,"it":3,"sh":[{"i":{"a":{"p":"M25.953,7.275c-2.58-2.534-6.645-2.382-9.38,0.3l-0.599,0.598l-0.599-0.599c-2.736-2.682-6.798-2.833-9.38-0.299c-2.583,2.531-2.735,6.699,0,9.38l9.979,9.879l10.079-9.879C28.788,13.974,28.538,9.806,25.953,7.275z","t":"","s":"none","fl":"#333"}},"f":{"20":{"t":"s1.2"},"90":{"t":""},"100":{}}}]},"sitemap":{"d":600,"it":1,"sh":[{"i":{"a":{"p":"M29,29h-6c-0.553,0-1-0.447-1-1v-6c0-0.553,0.447-1,1-1h6c0.553,0,1,0.447,1,1v6C30,28.553,29.553,29,29,29zM20,28v-6c0-0.553-0.447-1-1-1h-6c-0.552,0-1,0.447-1,1v6c0,0.553,0.448,1,1,1h6C19.553,29,20,28.553,20,28zM10,28v-6c0-0.553-0.448-1-1-1H3c-0.552,0-1,0.447-1,1v6c0,0.553,0.448,1,1,1h6C9.552,29,10,28.553,10,28zM19,13v-1h-2h-2h-2v1l-8,4v3h2v-2l8-4v6h2v-6l8,4v2h2v-3L19,13z","t":"t0,1","s":"none","fl":"#333"}},"f":{"0":{"p":"M16,14L16,14c-0.553,0-1-0.447-1-1l0,0c0-0.553,0.447-1,1-1l0,0c0.553,0,1,0.447,1,1l0,0C17,13.553,16.553,14,16,14zM17,13L17,13c0-0.553-0.447-1-1-1l0,0c-0.552,0-1,0.447-1,1l0,0c0,0.553,0.448,1,1,1l0,0C16.553,14,17,13.553,17,13zM17,13L17,13c0-0.553-0.447-1-1-1l0,0c-0.552,0-1,0.447-1,1l0,0c0,0.553,0.448,1,1,1l0,0C16.553,14,17,13.553,17,13zM19,13v-1h-2h-2h-2v1h2v1h2v-2h-2l0,0h2l0,0h-2v2h2v-1H19z"},"20":{"p":"M16,20L16,20c-0.553,0-1-0.447-1-1l0,0c0-0.553,0.447-1,1-1l0,0c0.553,0,1,0.447,1,1l0,0C17,19.553,16.553,20,16,20zM17,19L17,19c0-0.553-0.447-1-1-1l0,0c-0.552,0-1,0.447-1,1l0,0c0,0.553,0.448,1,1,1l0,0C16.553,20,17,19.553,17,19zM17,19L17,19c0-0.553-0.447-1-1-1l0,0c-0.552,0-1,0.447-1,1l0,0c0,0.553,0.448,1,1,1l0,0C16.553,20,17,19.553,17,19zM19,13v-1h-2h-2h-2v1l2,4v3h2v-2l-2-4v6h2v-6l-2,4v2h2v-3L19,13z"},"40":{"p":"M19,29h-6c-0.553,0-1-0.447-1-1v-6c0-0.553,0.447-1,1-1h6c0.553,0,1,0.447,1,1v6C20,28.553,19.553,29,19,29zM20,28v-6c0-0.553-0.447-1-1-1h-6c-0.552,0-1,0.447-1,1v6c0,0.553,0.448,1,1,1h6C19.553,29,20,28.553,20,28zM20,28v-6c0-0.553-0.447-1-1-1h-6c-0.552,0-1,0.447-1,1v6c0,0.553,0.448,1,1,1h6C19.553,29,20,28.553,20,28zM19,13v-1h-2h-2h-2v1l2,4v3h2v-2l-2-4v6h2v-6l-2,4v2h2v-3L19,13z"},"70":{"p":"M29,29h-6c-0.553,0-1-0.447-1-1v-6c0-0.553,0.447-1,1-1h6c0.553,0,1,0.447,1,1v6C30,28.553,29.553,29,29,29zM20,28v-6c0-0.553-0.447-1-1-1h-6c-0.552,0-1,0.447-1,1v6c0,0.553,0.448,1,1,1h6C19.553,29,20,28.553,20,28zM10,28v-6c0-0.553-0.448-1-1-1H3c-0.552,0-1,0.447-1,1v6c0,0.553,0.448,1,1,1h6C9.552,29,10,28.553,10,28zM19,13v-1h-2h-2h-2v1l-8,4v3h2v-2l8-4v6h2v-6l8,4v2h2v-3L19,13z"},"100":{}}},{"i":{"a":{"p":"M19,11h-6c-0.553,0-1-0.447-1-1V4c0-0.553,0.447-1,1-1h6c0.553,0,1,0.447,1,1v6C20,10.553,19.553,11,19,11z","s":"none","t":"t0,1","fl":"#333"}},"f":{}}]}}),lDI=lDI.replace(/\"d\":/g,'"duration":').replace(/\"i\":/g,'"init":').replace(/\"f\":/g,'"frames":').replace(/\"fIE\":/g,'"framesIE":').replace(/\"o\":/g,'"opacity":').replace(/\"t\":/g,'"transform":').replace(/\"it\":/g,'"iteration":').replace(/\"sh\":/g,'"shapes":').replace(/\"a\":/g,'"attr":').replace(/\"p\":/g,'"path":').replace(/\"fl\":/g,'"fill":').replace(/\"e\":/g,'"easing":').replace(/\"s\":/g,'"stroke-width":0,"stroke":'),liviconsdata=JSON.parse(lDI),sB=Raphael.svg,vB=Raphael.vml;
Raphael.fn.createLivicon=function(f,b,g,k,h,c,u,s,v,x,w,y,m){var e=[];g=clone(w);var d=g.shapes.length;s=s?s:g.iteration;var l=[],q=[],t=[],A="s"+y+","+y+",0,0";w=y=!1;if(b.match(/spinner/)){y=!0;var D=jQuery("#"+f),B=function(){if(D.is(":visible")){if(!z){for(var a=0;a< d;a++)e[a].animate(l[a].repeat(Infinity));z=!0}}else if(z){for(a=0;a< d;a++)e[a].stop();z=!1}}}b.match(/morph/)&&(w=!0);for(b=0;b< d;b++){var r=g.shapes[b].init,n;for(n in r)r[n].transform=A+r[n].transform}if(sB)for(b=0;b< d;b++)for(n in r=
g.shapes[b].frames,r)"transform"in r[n]&&(r[n].transform=A+r[n].transform);else for(b=0;b< d;b++)for(n in r=g.shapes[b].framesIE?g.shapes[b].framesIE:g.shapes[b].frames,r)"transform"in r[n]&&(r[n].transform=A+r[n].transform);for(b=0;b< d;b++)n=g.shapes[b].init.attr,"original"!=k&&(n.fill=k),t.push(n.fill),e[b]=this.path(n.path).attr(n);sB?jQuery("#"+f+" > svg").attr("id","canvas-for-"+f):jQuery("#"+f).children(":first-child").attr("id","canvas-for-"+f);f=jQuery("#"+f);m=m?m:f;if(!0==c){if(w){for(b=
0;b< d;b++)l.push(Raphael.animation(g.shapes[b].frames,mD)),q.push(g.shapes[b].init.attr);if(h){var C=clone(q);for(b=0;b< d;b++)C[b].fill=h}}else if(c=v?v:g.duration,!sB&&vB)for(b=0;b< d;b++)g.shapes[b].framesIE?l.push(Raphael.animation(g.shapes[b].framesIE,c)):l.push(Raphael.animation(g.shapes[b].frames,c)),q.push(g.shapes[b].init.attr);else for(b=0;b< d;b++)l.push(Raphael.animation(g.shapes[b].frames,c)),q.push(g.shapes[b].init.attr);if("click"==x)if(u&&!w)if(y){for(b=0;b<
d;b++)e[b].stop().animate(l[b].repeat(Infinity));var z=!0;setInterval(B,500)}else if(h){m.hover(function(){for(var a=0;a< d;a++)e[a].animate({fill:h},hD)},function(){for(var a=0;a< d;a++)e[a].animate({fill:t[a]},hD)});var p=!0;m.click(function(){for(var a=0;a< d;a++)e[a].stop().animate(p?l[a].repeat(u):q[a],0);p=!p})}else p=!0,m.click(function(){for(var a=0;a< d;a++)e[a].stop().animate(p?l[a].repeat(u):q[a],0);p=!p});else w?h?(m.hover(function(){for(var a=0;a< d;a++)e[a].animate({fill:h},
hD)},function(){for(var a=0;a< d;a++)e[a].animate({fill:t[a]},hD)}),p=!0,m.click(function(){for(var a=0;a< d;a++)e[a].stop().animate(p?l[a]:C[a],mD),p=!p})):(p=!0,m.click(function(){for(var a=0;a< d;a++)e[a].stop().animate(p?l[a]:q[a],mD),p=!p})):h?(m.hover(function(){for(var a=0;a< d;a++)e[a].animate({fill:h},hD)},function(){for(var a=0;a< d;a++)e[a].animate({fill:t[a]},hD)}),m.click(function(){for(var a=0;a< d;a++)e[a].stop().animate(l[a].repeat(s))})):
m.click(function(){for(var a=0;a< d;a++)e[a].stop().animate(l[a].repeat(s))});else if(u&&!w)if(y){for(x=0;x< d;x++)e[x].stop().animate(l[x].repeat(Infinity));z=!0;setInterval(B,500)}else h?m.hover(function(){for(var a=0;a< d;a++)e[a].stop().animate({fill:h},hD).animate(l[a].repeat(u))},function(){for(var a=0;a< d;a++)e[a].stop().animate(q[a],0)}):m.hover(function(){for(var a=0;a< d;a++)e[a].stop().animate(l[a].repeat(u))},function(){for(var a=0;a< d;a++)e[a].stop().animate(q[a],0)});else w?m.hover(function(){if(h)for(var a=
0;a< d;a++)e[a].stop().animate({fill:h},hD).animate(l[a]);else for(a=0;a< d;a++)e[a].stop().animate(l[a])},function(){for(var a=0;a< d;a++)e[a].stop().animate(q[a],mD)}):m.hover(function(){if(h)for(var a=0;a< d;a++)e[a].stop().animate(q[a],0).animate({fill:h},hD).animate(l[a].repeat(s));else for(a=0;a< d;a++)e[a].stop().animate(q[a],0).animate(l[a].repeat(s))},function(){for(var a=0;a< d;a++)e[a].animate({fill:t[a]},hD)})}else h&&m.hover(function(){for(var a=
0;a< d;a++)e[a].stop().animate({fill:h},hD)},function(){for(var a=0;a< d;a++)e[a].stop().animate({fill:t[a]},hD)});return!0};
(function(f){function b(){return b.counter++}b.counter=1;f.fn.extend({addLivicon:function(g){return this.each(function(){var k=f(this);if(!k.attr("id")){var h=b();k.attr("id","livicon-"+h)}var c=k.data();c.liviconRendered&&k.removeLivicon();c=fullNames(c);g&&(g=fullNames(g));var c=f.extend(c,g),h=k.attr("id"),u=k.parent(),s=c.name?c.name:dN,v=c.size?c.size:dS,x=c.eventtype?c.eventtype:dET,w=v/32;k[0].style.height?k.css("width",v):k.css({width:v,height:v});var y=s in liviconsdata?
liviconsdata[s]:liviconsdata[dN],m=k.hasClass(aC)||u.hasClass(aPC)?dAC:"original"==c.color?"original":c.color?c.color:dC,e=dA?!1==c.animate?c.animate:dA:!0==c.animate?c.animate:dA,d=dL?!1==c.loop?!1:Infinity:!0==c.loop?Infinity:!1,l=c.iteration?0< Math.round(c.iteration)?Math.round(c.iteration):!1:!1,q=c.duration?0< Math.round(c.duration)?Math.round(c.duration):!1:!1,t=dCCOH?dHC:!1;!1===c.hovercolor||
0===c.hovercolor?t=!1:!0===c.hovercolor||1===c.hovercolor?t=dHC:c.hovercolor&&(t=c.hovercolor);c=dOP?!1==c.onparent?!1:u:!0==c.onparent?u:!1;Raphael(h,v,v).createLivicon(h,s,v,m,t,e,d,l,q,x,y,w,c);k.data("liviconRendered",!0);return this})},removeLivicon:function(b){return this.each(function(){var k=f(this);k.data("liviconRendered",!1);if("total"===b)k.remove();else{var h=k.attr("id");f("#canvas-for-"+h).remove();return k}})},updateLivicon:function(b){return this.each(function(){var k=
f(this);k.removeLivicon().addLivicon(b);return k})}});f(".livicon").addLivicon()})(jQuery);function fullNames(f){f=JSON.stringify(f);f=f.replace(/\"n\":/g,'"name":').replace(/\"s\":/g,'"size":').replace(/\"c\":/g,'"color":').replace(/\"hc\":/g,'"hovercolor":').replace(/\"a\":/g,'"animate":').replace(/\"i\":/g,'"iteration":').replace(/\"d\":/g,'"duration":').replace(/\"l\":/g,'"loop":').replace(/\"et\":/g,'"eventtype":').replace(/\"op\":/g,'"onparent":');return f=JSON.parse(f)}
function clone(f){if(null==f||"object"!=typeof f)return f;var b=new f.constructor,g;for(g in f)b[g]=clone(f[g]);return b};});
