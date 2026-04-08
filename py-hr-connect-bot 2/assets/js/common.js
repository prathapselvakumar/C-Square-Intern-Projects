function ajaxPostJsonSync(url, data){
    response = null;
    $.ajax({
        url: url,
        type: 'post',
        async: false,
        dataType: 'json',
        contentType: 'application/json',
        data: JSON.stringify(data),
        success: function (resp) {
            response = resp;
        }
    });
    return response;
}


function ajaxGetSync(url){
    response = null;
    $.ajax({
        url: url,
        type: 'get',
        async: false,
        dataType: 'json',
        contentType: 'application/json',
        success: function (resp) {
            response = resp;
        }
    });
    return response;
}