jQuery(document).ajaxSend(function(event, xhr, settings) {
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    function sameOrigin(url) {
        // url could be relative or scheme relative or absolute
        var host = document.location.host; // host + port
        var protocol = document.location.protocol;
        var sr_origin = '//' + host;
        var origin = protocol + sr_origin;
        // Allow absolute or scheme relative URLs to same origin
        return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
            (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
            // or any other URL that isn't scheme relative or absolute i.e relative.
            !(/^(\/\/|http:|https:).*/.test(url));
    }
    function safeMethod(method) {
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    if (!safeMethod(settings.type) && sameOrigin(settings.url)) {
        xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
    }
});

(function () {
    $(document).ready(function () {
        $('.session').each(function (i, session) {
            session = $(session);
            var unallocated = JSON.parse(session.attr('data-archers'));

            var initializeInput = function (input) {
                input = $(input);
                input.autocomplete({
                    source: function (request, response) {
                        response($.ui.autocomplete.filter(unallocated, request.term));
                    },
                    delay: 0,
                    select: function (e, ui) {
                        console.log(input.attr('data-location'), ui.item.pk);
                        input.blur();
                        var index = undefined;
                        $.each(unallocated, function (i, entry) {
                            if (entry.pk === ui.item.pk) {
                                index = i;
                            }
                        });
                        unallocated.splice(index, 1);
                        // Remove the name from the unallocated list
                        var el = $(this);
                        el.closest('.session').find('.unallocated [data-pk='+ui.item.pk+']').remove();
                        // Focus the next input (wherever it is)
                        var inputs = el.closest('.session').find('input');
                        var index = inputs.index(el);
                        if (index > -1 && (index + 1) < inputs.length) {
                            inputs.eq(index + 1).focus();
                        }
                        $.post(
                            '',
                            JSON.stringify({method: 'create', entry: ui.item.pk, location: input.attr('data-location')}),
                            function (data) {
                                // Replace this input with a label
                                var archerSpan = $('<span>');
                                archerSpan.text(ui.item.value);
                                archerSpan.addClass('archer');
                                var link = $('<a>');
                                link.text('X');
                                link.attr('data-entry-pk', ui.item.pk);
                                link.attr('data-pk', data);
                                link.addClass('delete');
                                link.click(deleteAllocation);
                                el.replaceWith(archerSpan);
                                archerSpan.after(link);
                            }
                        );
                    }
                });
            };

            var deleteAllocation = function (e) {
                var el = $(this);
                $.post(
                    '',
                    JSON.stringify({method: 'delete', entry: el.attr('data-pk')}),
                    function () {
                        var input = $('<input>');
                        input.attr('data-location', el.attr('data-location'));
                        var archer = el.siblings('.archer');
                        unallocated.push({'pk': el.attr('data-entry-pk'), 'value': archer.text()});
                        var li = $('<li>');
                        li.text(archer.text());
                        li.attr('data-pk', el.attr('data-entry-pk'));
                        el.closest('.session').find('.unallocated').append(li);
                        el.replaceWith(input);
                        archer.remove();
                        initializeInput(input);
                    }
                )
            };

            session.find('input').each(function (i, input) {initializeInput(input)});
            session.find('a.delete').click(deleteAllocation);
        });
    });
})();
