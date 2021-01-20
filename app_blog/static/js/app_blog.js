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
