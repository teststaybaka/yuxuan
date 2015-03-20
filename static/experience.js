$(document).ready(function() {
    var url = document.URL;
    var page = 1;
    var isLoading = false;
    $(window).scroll(function() {
        if(($(window).scrollTop() >= $(document).height() - $(window).height()) && !isLoading) {
            isLoading = true;
            $('#main-body').append('<div class="preview-article loading"></div>');
            $.ajax({
                type: "POST",
                url: url+'?page='+(page+1),
                success: function(result) {
                    isLoading = false;
                    $('div.preview-article.loading').remove();
                    if(!result.error) {
                        for (var i = 0; i < result.articles.length; i++) {
                            article = result.articles[i];
                            var div = '<div class="preview-article">\
                                <div class="time-circle"></div>\
                                <div class="time-line"></div>\
                                <div class="preview-title-line">\
                                    <div class="preview-date">' + article.date + '</div>\
                                    <a class="preview-title black-link" href="/article/' + article.id + '">' + article.title + '</a>\
                                </div>'
                            if (article.image) {
                                div += '<div class="preview-image"><img class="preview-image" src="' + article.image + '"></div>'
                            }
                            div += '<div class="preview-content">' + article.content + '</div>\
                                <a class="read-more blue-link" href="/article/' + article.id + '">Read more >></a>\
                            </div>'
                            $('#main-body').append(div);
                        }
                        if (result.articles.length != 0) {
                            page++;
                        }
                    } else {
                        pop_ajax_message(result.message, 'error');
                    }
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
