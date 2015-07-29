jQuery(document).ready(function ($) {
    $('td input').each(function (i, input) {
        var input = $(input);
        var val = input.val();
        if (val == '0') { val = 'M' }
        if (val == '') { val = '&nbsp' }
        var fake = $('<span>').html(val);
        fake.addClass('fake-input');
        input.after(fake);
        if (i == 0) {   
            input.parent().addClass('active');
        }
    });

    var tablePress = function (e) {
        $('table .active').removeClass('active');
        $(this).addClass('active');
    };
    $('table .field').on('touchstart', tablePress);
    $('table .field').on('click', tablePress);

    var buttonPress = function (e) {
        e.preventDefault();
        var input = $('table .active input');
        if (!input.length) {
            return;
        }
        input.attr('value', $(this).attr('data-value'));
        var fake = input.next();
        fake.html($(this).attr('data-value'));
        arrows.updateTotals();
        input.parent().removeClass('active');
        var inputs = $('table input');
        inputs.each(function (i, other_input) {
            if (input.attr('name') == other_input.name) {
                if (inputs[i+1]) {
                    $(inputs[i+1]).parent().addClass('active');
                }
            }
        });
    };
    $('.input-buttons .input').on('touchstart', buttonPress);
    $('.input-buttons .input').on('click', buttonPress);
});
