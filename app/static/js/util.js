// General-purpose AJAX request wrapper using jQuery
function makeAjaxRequest(method, url, data) {
    return $.ajax({
        type: method,
        url: url,
        data: JSON.stringify(data),
        headers: {
            // Add CSRF token from <meta> tag for security
            "X-CSRFToken": $("meta[name='csrf-token']").attr("content"),
        },
        dataType: "json",
        contentType: "application/json",
    });
}
// Helper function to send a GET request with JSON payload
export function jsonApiGet(url, data) {
    return makeAjaxRequest("GET", url, data);
}
// Helper function to send a POST request with JSON payload
export function jsonApiPost(url, data) {
    return makeAjaxRequest("POST", url, data);
}