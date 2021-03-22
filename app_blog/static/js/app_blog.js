function add_headers() {
  var csrf = document.querySelector("input[name=csrfmiddlewaretoken]").value;
  var headers = new Headers();
  headers.append('X-Requested-With', 'XMLHttpRequest');
  headers.append('X-CSRFToken', csrf);
  return headers;
}

window.POST = function(url, data) {
  return fetch(url, {method: "POST", headers: add_headers(), body: JSON.stringify(data)});
}

window.GET = function(url) {
	return fetch(url)
}

function close_bs_alert() {
  var alertNode = document.querySelectorAll('.alert');
  alertNode.forEach(function(alertElem) {
    let alert = new bootstrap.Alert(alertElem);
    alert.close();
  })
}

function navbar_hide_title() {
  let title = document.getElementById("navbar-brand-title");
  let button = document.getElementsByClassName("navbar-toggler")[0];
  let isExpanded = button.getAttribute('aria-expanded');
  if (isExpanded === "true") {
    title.style = "display: inline;";
  } else {
    title.style = "display: none;";
  }
}
/* functions called when window is loaded */
function auto_close_bs_alert() {
  setTimeout(close_bs_alert, 3000);
}

function navbar_responsive() {
  var navbarToggler = document.getElementsByClassName("navbar-toggler")[0];
  navbarToggler.addEventListener('click', navbar_hide_title);
}

window.addEventListener('load', function () {
    auto_close_bs_alert();
    navbar_responsive();
  }
);