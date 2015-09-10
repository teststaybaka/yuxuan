$(document).ready(function() {
    var cursor = $('#cursor').val();
    if (!cursor) {
        return
    }

    var isLoading = false;
    var isOver = false;
    $(window).scroll(function() {
        if(($(window).scrollTop() >= $(document).height() - $(window).height() - 20) && !isLoading && !isOver) {
            isLoading = true;
            $('#main-body').append('<div class="preview-article loading"></div>');
            $.ajax({
                type: "POST",
                url: document.location.href,
                data: {cursor: cursor},
                success: function(result) {
                    $('div.preview-article.loading').remove();
                    if(!result.error) {
                        for (var i = 0; i < result.articles.length; i++) {
                            article = result.articles[i];
                            var div = '<div class="preview-article">\
                                <div class="time-circle"></div>\
                                <div class="time-line"></div>\
                                <div class="preview-title-line">\
                                    <div class="preview-date">' + article.date + '</div>\
                                    <a class="preview-title black-link" href="/article/' + result.cur_category + '/' + article.index + '">' + article.title + '</a>\
                                </div>'
                            if (article.image) {
                                div += '<div class="preview-image"><img class="preview-image" src="' + article.image + '"></div>'
                            }
                            div += '<div class="preview-content">' + article.content + '</div>\
                                <a class="read-more blue-link" href="/article/' + result.cur_category + '/' + article.index + '">Read more >></a>\
                            </div>'
                            $('#main-body').append(div);
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
    });
});
