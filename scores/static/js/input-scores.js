window.addEvent('domready', function () {
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
    if ($$('[data-focus]')) {
        var focus = $$('[data-focus]')[0].dataset['focus']
        $$('[rel=' + focus + ']')[0].fireEvent('keydown', {key: 'right', stop: function () {}});
    }
});
