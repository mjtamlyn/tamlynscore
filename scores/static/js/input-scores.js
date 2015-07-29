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
        $$('.input-board').removeClass('selected');
        board.addClass('selected');
        board.getElement('.boss-link')[0].focus();
    });

    $$('.boss-link').addEvent('keydown', function (e) {
        if (e.key == 'left') {
            e.stop();
            target = this.getPrevious('.boss-link');
            if (target) {
                target.focus();
            } else {
                nextBosses = this.getParent('.bosses').getPrevious('.bosses');
                if (nextBosses) {
                    nextBosses.getLast('.boss-link').focus();
                }
            }
        }
        if (e.key == 'right') {
            e.stop();
            target = this.getNext('.boss-link');
            if (target) {
                target.focus();
            } else {
                nextBosses = this.getParent('.bosses').getNext('.bosses');
                if (nextBosses) {
                    nextBosses.getElement('.boss-link').focus();
                }
            }
        }
        if (e.key == 'up') {
            e.stop();
            nextBosses = this.getParent('.bosses').getPrevious('.bosses');
            if (nextBosses) {
                nextBosses.getLast('.boss-link').focus();
            }
        }
        if (e.key == 'down') {
            e.stop();
            nextBosses = this.getParent('.bosses').getNext('.bosses');
            if (nextBosses) {
                nextBosses.getElement('.boss-link').focus();
            }
        }
    });

    $$('.boss-link')[0].focus();
    if (document.location.hash) {
        $$('a[href=' + document.location.hash.replace('#!', '#') + ']').fireEvent('click');
        $$('a[href=' + document.location.hash.replace('#!', '#').replace(/-round-\d/, '') + ']').fireEvent('click');
    }
    if ('{{ focus }}') {
        $$('[rel={{ focus }}]')[0].fireEvent('keydown', {key: 'right', stop: function () {}});
    }

});