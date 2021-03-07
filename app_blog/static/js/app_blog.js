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

function auto_close_bs_alert() {
  setTimeout(close_bs_alert, 3000);
}

window.addEventListener('load', auto_close_bs_alert);
