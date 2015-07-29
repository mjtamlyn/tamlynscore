window.addEvent('domready', function () {
    $$('.session-select a').addEvent('click', function (e) {
        if (e) { e.stop(); }
        // do this row
        $$('.session-select .link').removeClass('selected');
        this.getElement('.link').addClass('selected');
        // do the round select row
        $$('.round-select').removeClass('selected');
        var newRoundSelect = $$(this.get('href'));
        newRoundSelect.addClass('selected');
        newRoundSelect.getElement('.selected').getParent('a').fireEvent('click');
    });

    $$('.round-select a').addEvent('click', function (e) {
        if (e) { e.stop(); }
        // do this row
        this.getParent('.round-select').getElements('.link').removeClass('selected');
        this.getElement('.link').addClass('selected');
        // do the generator
        target = this.get('href');
        var board = $$(target);
        document.location.hash = target.replace('#', '#!');
        $$('.board').removeClass('selected');
        board.addClass('selected');
    });

    if (document.location.hash) {
        $$('a[href=' + document.location.hash.replace('#!', '#') + ']').fireEvent('click');
        $$('a[href=' + document.location.hash.replace('#!', '#').replace(/-round-\d/, '') + ']').fireEvent('click');
    }

    $$('.select-all').addEvent('change', function () {
        checkboxes = this.getParent('.board').getElement('table').getElements('input[type=checkbox]');
        if (this.get('value') === 'on') {
            checkboxes.set('checked', 'checked');
        } else {
            checkboxes.set('checked', '');
        }
    });
});
