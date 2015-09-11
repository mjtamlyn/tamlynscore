$('.archer-block .entries').each(function(i, item) {
    var $item = $(item);
    $item.find('a.reveal').click(function(e) {
        e.preventDefault();
        $item.find('ul').toggleClass('open');
    });
});
