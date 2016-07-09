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
    CKEDITOR.replace('editor');
    CKEDITOR.instances['editor'].setData($('#original-content').html());
    $('#preview-button').click(function() {
        for ( instance in CKEDITOR.instances ) {
            CKEDITOR.instances[instance].updateElement();
        }
        $('#MathOutput').html($('#editor').val());
        MathJax.Hub.Queue(
            ["resetEquationNumbers",MathJax.InputJax.TeX],
            ['Typeset',MathJax.Hub,'MathOutput']
        );
    });

    $('form').on('click', 'div.remove-image', function() {
        var safe_url = $(this).siblings('input.safe-url').val();
        $(this).parent().remove();
        if (!safe_url) return;

        console.log(safe_url)
        $.ajax({
            type: 'POST',
            url: '/image_remove',
            data: {safe_url: safe_url},
            success: function(result) {
                console.log(result);
            },
            error: function (xhr, ajaxOptions, thrownError) {
                console.log(xhr.status);
                console.log(thrownError);
                pop_ajax_message('Error', 'error');
            }
        });
        
    });

    $('#add-more').click(function() {
        $('#add-more-line').before('<div class="file-input-line">\
                <input type="file" class="image-file">\
                <div class="remove-image">Remove</div>\
                <label class="image-url"></label>\
                <input type="text" class="safe-url" name="images[]" hidden>\
            </div>');
    });

    $('form').on('change', 'input.image-file', function() {
        var input_file = $(this);
        var file = input_file[0].files[0];
        if (file) {
            $.ajax({
                type: 'POST',
                url: '/upload_url',
                success: function(result) {
                    var formData = new FormData();
                    formData.append('image', file);
                    $.ajax({
                        type: 'POST',
                        url: result,
                        data: formData,
                        cache: false,
                        contentType: false,
                        processData: false,
                        success: function(result) {
                            // console.log(result)
                            var url = result.url;
                            var safe_url = result.safe_url;
                            input_file.siblings('label.image-url').text(url);
                            input_file.siblings('input.safe-url').val(safe_url);
                        },
                        error: function (xhr, ajaxOptions, thrownError) {
                            console.log(xhr.status);
                            console.log(thrownError);
                            pop_ajax_message('Error', 'error');
                        }
                    });
                },
                error: function (xhr, ajaxOptions, thrownError) {
                    console.log(xhr.status);
                    console.log(thrownError);
                    pop_ajax_message('Error', 'error');
                }
            });
        }
    });

    $('form').submit(function(evt) {
        for ( instance in CKEDITOR.instances ) {
            CKEDITOR.instances[instance].updateElement();
        }
        $.ajax({
            type: 'POST',
            url: evt.target.action, 
            data: $(evt.target).serialize(), 
            success: function(result) {
                pop_ajax_message(result.message, result.type);
            },
            error: function (xhr, ajaxOptions, thrownError) {
                console.log(xhr.status);
                console.log(thrownError);
                pop_ajax_message('Error', 'error');
            }
        });
        return false;
    });
});
