var csrf = document.querySelector("input[name=csrfmiddlewaretoken]").value
var headers = new Headers();
headers.append('X-Requested-With', 'XMLHttpRequest');
headers.append('X-CSRFToken', csrf)

window.POST = function(url, data) {
  return fetch(url, {method: "POST", headers: headers, body: JSON.stringify(data)});
}

window.GET = function(url) {
	return fetch(url)
}


var navbarDropdownItemList = document.querySelectorAll("#navbarSupportedContent > ul.navbar-nav > li.dropdown > ul.dropdown-menu > li > a");

navbarDropdownItemList.forEach(function(elem) {
    elem.addEventListener("click", function() {
		POST("/get_category", {name: elem.name});
    });
});
