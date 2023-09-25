function replaceWhiteSelects(divElement) {
  divElement = divElement || document;
  var x, i, j, selElmnt, a, b, c, option, idx, lastLetter, currentLetter;
  /*look for any elements with the class "white-border-select":*/
  x = divElement.getElementsByClassName("white-border-select");
  for (i = 0; i < x.length; i++) {
    var currentSelect = x[i];
    selElmnt = currentSelect.getElementsByTagName("select")[0];
    //if(!selElmnt){
    //  selElmnt = $('#white-select-fix')[0];
    //}
    /*for each element, create a new DIV that will act as the selected item:*/
    a = document.createElement("DIV");
    a.setAttribute("class", "select-selected");
    a.setAttribute("tabindex", i);
    a.innerHTML = selElmnt.options[selElmnt.selectedIndex].innerHTML;
    // Set tooltip while getting rid of any extra white spaces
    a.setAttribute("title", a.innerHTML.replace(/\s+/g, " ").trim());
    currentSelect.appendChild(a);
    /*for each element, create a new DIV that will contain the option list:*/
    b = document.createElement("DIV");
    b.setAttribute("class", "select-items select-hide");
    b.setAttribute("tabindex", i);
    $(b).keypress(function(e) {
      console.log(e.keyCode);
      if (e.keyCode == 13) {
        $(this).click();
      } else if (e.keyCode == 27) {
        $(a).click();
      }
    });
    var firstIsTitle = currentSelect.classList.contains('firstistitle');
    var start_j = 0;
    if (firstIsTitle) {
        start_j= 1;
    }
    for (j = start_j; j < selElmnt.length; j++) {
      /*for each option in the original select element,
          create a new DIV that will act as an option item:*/
      c = document.createElement("DIV");
      c.setAttribute("tabindex", i);
      option = selElmnt.options[j];
      c.innerHTML = option.innerHTML;
      $(c).keypress(function(e) {
        if (e.keyCode == 13) {
          $(this).click();
        }
      });
      if (option.getAttribute("noSelect") === "1") {
        continue;
      }

      c.setAttribute("value", option.getAttribute("value"));

      if ($(currentSelect).hasClass("white-border-multiline")) {
        c.innerHTML = "";
        var lines = option.innerHTML.split("#");
        lines.forEach(function(text) {
          var linediv = document.createElement("span");
          linediv.innerHTML = text;
          c.appendChild(linediv);
        });
      }

      c.addEventListener("click", function(e) {
        /*when an item is clicked, update the original select box,
              and the selected item:*/
        var y, i, k, s, h;
        s = this.parentNode.parentNode.getElementsByTagName("select")[0];
        h = this.parentNode.previousSibling;
        for (i = 0; i < s.length; i++) {
          var value = this.getAttribute("value");
          if (s.options[i].value === value) {
            s.selectedIndex = i;
            $(s).trigger("change");
            h.innerHTML = this.innerHTML;
            y = this.parentNode.getElementsByClassName("same-as-selected");
            for (k = 0; k < y.length; k++) {
              y[k].removeAttribute("class");
            }
            this.setAttribute("class", "same-as-selected");
            break;
          }
        }
        h.click();
      });
      b.appendChild(c);
    }
    currentSelect.appendChild(b);
    a.addEventListener("click", function(e) {
      /*when the select box is clicked, close any other select boxes,
          and open/close the current select box:*/
      e.stopPropagation();
      closeAllSelect(this);
      this.nextSibling.classList.toggle("select-hide");
      this.classList.toggle("select-arrow-active");
      document.removeEventListener("keyup", goToSelection);
      if ($(this).hasClass("select-arrow-active")) {
        idx = 0;
        document.addEventListener("keyup", goToSelection);
      }
    });
  }
  function closeAllSelect(elmnt) {
    /*a function that will close all select boxes in the document,
      except the current select box:*/
    var x,
      y,
      i,
      arrNo = [];
    x = divElement.getElementsByClassName("select-items");
    y = divElement.getElementsByClassName("select-selected");
    for (i = 0; i < y.length; i++) {
      if (elmnt == y[i]) {
        arrNo.push(i);
      } else {
        y[i].classList.remove("select-arrow-active");
      }
    }
    for (i = 0; i < x.length; i++) {
      if (arrNo.indexOf(i)) {
        x[i].classList.add("select-hide");
      }
    }
  }
  function goToSelection(event) {
    currentLetter = String.fromCharCode(event.keyCode);
    if (lastLetter == undefined || currentLetter != lastLetter) {
      idx = 0;
    } else {
      idx = idx + 1;
    }
    currentLetter = String.fromCharCode(event.keyCode);
    let activeSelect = $(".select-arrow-active");
    let activeItemsList = activeSelect.next(".select-items");
    let activeItems = activeItemsList.find("div");
    let outerSize = $(activeItems[0]).outerHeight();
    let newList = [];
    newList = activeItems.map(function(element) {
      if (
        $(this)
          .text()
          .startsWith(currentLetter)
      ) {
        return element;
      }
    });
    if (newList.length != 0) {
      if (idx != newList.length) {
        offset = newList[idx];
      } else {
        idx = 0;
        offset = newList[idx];
      }
      activeItemsList.scrollTop(offset * outerSize);
    }
    lastLetter = currentLetter;
  }
  /*if the user clicks anywhere outside the select box,
    then close all select boxes:*/
  divElement.addEventListener("click", closeAllSelect);

  $(".select-selected").keypress(function(e) {
    if (e.keyCode == 13) {
      $(this).click();
    }
  });
}

function makeButtonsTabbables() {
  x = document.getElementsByClassName("white-border-button");

  for (i = 0; i < x.length; i++) {
    var currentSelect = x[i];
    currentSelect.setAttribute("tabindex", 0);
    $(currentSelect).keypress(function(e) {
      if (e.keyCode == 13) {
        $(this).click();
      }
    });
  }
}

$().ready(() => {
  makeButtonsTabbables();
});
replaceWhiteSelects();
