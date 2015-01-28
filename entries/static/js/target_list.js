(function () {
    $(document).ready(function () {
        $('.session').each(function (i, session) {
            session = $(session);
            var unallocated = JSON.parse(session.attr('data-archers'));
            unallocated.unshift({
                id: '-1',
                text: 'Select…',
            });

            var initializeInput = function () {
                var originalAnchor = $(this);
                var select = $('<select>');
                originalAnchor.replaceWith(select);
                select.select2({
                    data: unallocated,
                    // TODO: Add a custom matcher to make searching easier
                    width: '70%',
                    templateSelection: function(item) {
                        return item.name || item.text;
                    },
                    templateResult: function(item) {
                        if (!item.bowstyle) {
                            return item.text;
                        }
                        text = (
                            item.name + '<br>' +
                            item.club + '<br>' +
                            '<span class="pill bowstyle ' + item.bowstyle.toLowerCase() + '">'
                                + item.bowstyle + '</span> ' +
                            '<span class="pill gender ' + item.gender.toLowerCase() + '">'
                                + item.gender + '</span>'
                        )
                        // TODO: support competition options properly
                        return text;
                    },
                });
                select.select2('open');
                select.on('select2:close', function (e) {
                    if (select.val() == '-1') {
                        select.select2('destroy');
                        select.replaceWith(originalAnchor);
                    }
                });
                select.on('select2:select', function (e) {
                    var archerBlock = $(this).closest('.archer-block');
                    var loc = archerBlock.attr('data-location');
                    var data = e.params.data;
                    select.select2('destroy');
                    select.replaceWith(originalAnchor);

                    // Remove the name from the unallocated list
                    archerBlock.closest('.session').find('.unallocated [data-pk=' + data.id + ']').remove();

                    $.post('', JSON.stringify({
                            method: 'create',
                            entry: data.id,
                            location: loc,
                        }), function () {
                            var index = undefined;
                            unallocated.forEach(function(item, i) {
                                if (item.id == data.id) {
                                    index = i;
                                }
                            });
                            unallocated.splice(index, 1);
                            originalAnchor.replaceWith('<span class="name">' + data.name + '</span>');
                            archerBlock.find('.bottom').html(
                                '<p>' + data.club + '</p><p>' +
                                '<span class="pill bowstyle ' + data.bowstyle.toLowerCase() + '">'
                                    + data.bowstyle + '</span> ' +
                                '<span class="pill gender ' + data.gender.toLowerCase() + '">'
                                    + data.gender + '</span></p>'
                                // TODO: don't duplicate code here
                            );
                            archerBlock.find('.actions').append($('<a class="delete" data-pk="' + data.id + '">X</a>'));
                        }
                    );
                });
                var opts = {
                    select: function (e, ui) {
                        // Focus the next input (wherever it is)
                        var inputs = el.closest('.session').find('input');
                        var index = inputs.index(el);
                        if (index > -1 && (index + 1) < inputs.length) {
                            inputs.eq(index + 1).focus();
                        }
                    }
                };
            };

            var deleteAllocation = function (e) {
                var el = $(this);
                var archerBlock = el.closest('.archer-block');
                $.post('',
                    JSON.stringify({
                        method: 'delete',
                        session_entry: el.attr('data-pk'),
                    }), function () {
                        archerBlock.find('.bottom').empty();
                        el.remove();
                        archerBlock.find('span.name').replaceWith('<a class="select">Select…</a>');
                        // TODO: readd the archer block to the bottom
                        // TODO: readd the details to the unallocated data
                    }
                )
            };

            session.on('click', '.select', initializeInput);
            session.on('click', '.actions .delete', deleteAllocation);
        });
    });
})();
