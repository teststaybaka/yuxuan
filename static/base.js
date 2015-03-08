function numberWithCommas(x) {
    var parts = x.toString().split(".");
    parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    return parts.join(".");
}

function pop_ajax_message(content, type) {
     $('#ajax-message-box').append('<div class="ajax-message '+type+'"> \
            <div class="ajax-icon '+type+'"></div> \
            <div class="ajax-content">'+content+'</div> \
        </div>');

    var lasts = $('div.ajax-message:last-child');
    lasts.height(lasts[0].scrollHeight);
    // console.log(lasts[0].scrollHeight);

    setTimeout(function() {
        lasts.height(0);
        setTimeout(function() {
            lasts.remove();
        }, 280);
    }, 5000);
}

$(document).ready(function() {
    $('form').submit(function(evt) {
        $('input.button').prop('disabled', true);
        $.ajax({
            type: 'POST',
            url: evt.target.action, 
            data: $(evt.target).serialize(), 
            success: function(result) {
                pop_ajax_message(result.message, result.type);
                $('input.button').prop('disabled', false);
            },
            error: function (xhr, ajaxOptions, thrownError) {
                console.log(xhr.status);
                console.log(thrownError);
                pop_ajax_message('Submit error.', 'error');
                $('input.button').prop('disabled', false);
            }
        });
        return false;
    });

    $('div.preview-content').each(function() {
        $(this).find('img').remove();
    });
    $('div.preview-content').dotdotdot();

    $('span.comments-num').each(function() {
        $(this).text(numberWithCommas($(this).text()) );
    });
});
