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
