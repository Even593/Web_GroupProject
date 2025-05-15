function makeAjaxRequest(method, url, data) {
    return $.ajax({
        type: method,
        url: url,
        data: JSON.stringify(data),
        headers: {
            "X-CSRFToken": $("meta[name='csrf-token']").attr("content"),
        },
        dataType: "json",
        contentType: "application/json",
    });
}

export function jsonApiGet(url, data) {
    return makeAjaxRequest("GET", url, data);
}

export function jsonApiPost(url, data) {
    return makeAjaxRequest("POST", url, data);
}