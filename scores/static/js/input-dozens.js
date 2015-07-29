$(document).ready(function () {
    $('input')[0].focus();
    $('.doz-total input').keyup(function () {
        var input = $(this);
        var rt = input.closest('tr').find('.rt');
        var initialValue = parseInt(rt.attr('rel'));
        if (isNaN(initialValue)) {
            initialValue = 0;
        }
        var value = parseInt(input.val());
        if (isNaN(value)) {
            value = 0;
        }
        var total = initialValue + value;
        rt.html(total);
    });
    $('input').trigger('keyup')
});