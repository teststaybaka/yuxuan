$(document).ready(function() {
    var cursor = $('#cursor').val();
    if (!cursor) {
        return
    }

    var isLoading = false;
    var isOver = false;
    $(window).scroll(loadMore);
    
    function loadMore() {
        if(($(window).scrollTop() >= $(document).height() - $(window).height() - 20) && !isLoading && !isOver) {
            isLoading = true;
            $('.left-column').append('<div class="preview-article loading"></div>');
            $.ajax({
                type: "POST",
                url: document.location.href,
                data: { cursor: cursor },
                success: function(result) {
                    $('.preview-article.loading').remove();
                    if(!result.error) {
                        for (var i = 0; i < result.articles.length; i++) {
                            article = result.articles[i];
                            var div = '<div class="preview-article">\
                                <div class="time-circle"></div>\
                                <div class="time-line"></div>\
                                <a class="preview-link" href="/'+article.category+'/'+article.index+'">\
                                    <div class="preview-title">' + article.title + '</div>\
                                    <div class="preview-date">' + article.date + '</div>'
                            if (article.image) {
                                div += '<div class="preview-image"><img class="preview-image" src="' + article.image + '"></div>'
                            }
                            div += '<div class="preview-content">' + article.content + '</div>\
                                </a>\
                            </div>'
                            $('.left-column').append(div);
                        }
                        isOver = !result.cursor;
                        cursor = result.cursor;
                    } else {
                        pop_ajax_message(result.message, 'error');
                    }
                    isLoading = false;
                },
                error: function (xhr, ajaxOptions, thrownError) {
                    isLoading = false;
                    $('div.preview-article.loading').remove();
                    console.log(xhr.status);
                    console.log(thrownError);
                    pop_ajax_message(xhr.status+' '+thrownError, 'error');
                }
            });
        }
    }
});
