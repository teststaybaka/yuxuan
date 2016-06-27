function numberWithCommas(x) {
    var parts = x.toString().split(".");
    parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    return parts.join(".");
}

$(document).ready(function() {
    $('div.preview-content').dotdotdot();
    $('span.comments-num').each(function() {
        $(this).text(numberWithCommas($(this).text()) );
    });

    var url = window.location.href;
    var parts = url.split('/');
    if (parts[3] === '') {
        $('.navi-entry.home').addClass('active');
    } else {
        $('.navi-entry.'+parts[3]).addClass('active');
    }

    (function(d, s, id) {
        var js, fjs = d.getElementsByTagName(s)[0];
        if (d.getElementById(id)) return;
        js = d.createElement(s); js.id = id;
        js.src = "//connect.facebook.net/en_US/sdk.js#xfbml=1&version=v2.6";
        fjs.parentNode.insertBefore(js, fjs);
    }(document, 'script', 'facebook-jssdk'));
});
