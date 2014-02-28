var Arrows = new Class({
    validCodes: {
        '48': '10', // 0 key
        '49': '1',
        '50': '2',
        '51': '3',
        '52': '4',
        '53': '5',
        '54': '6',
        '55': '7',
        '56': '8',
        '57': '9',
        '88': 'X', // x key
        '189': 'X', // - key
        '77': 'M', // m key
        '192': 'M', // ` key
        '223': 'M', // ` key (alternative code)
        // keypad keys
        '96': 'M', // keypad 0
        '97': '1',
        '98': '2',
        '99': '3',
        '100': '4',
        '101': '5',
        '102': '6',
        '103': '7',
        '104': '8',
        '105': '9',
        '110': '10', // keypad 10
    },

    initialize: function () {
        this.dirMap = {
            'up': this.move.pass('up').bind(this),
            'down': this.move.pass('down').bind(this),
            'left': this.move.pass('left').bind(this),
            'right': this.move.pass('right').bind(this),
        }
    },

    setUp: function () {
        $$('input')[0].focus();
        $$('input').each(function (item, index, array) {
            if (item.get('type') !== 'text') {
                return;
            }
            item.addEvent('keydown', function (e) {
                if (e.code in this.validCodes) {
                    item.set('value', this.validCodes[e.code]);
                    if (array[index + 1]) {
                        array[index + 1].focus();
                    }
                    this.updateTotals(item);
                    e.stop();
                }
                if (e.key in this.dirMap) {
                    this.dirMap[e.key]();
                    e.stop();
                }
                if (e.code == 8) { // backspace
                    item.set('value', '');
                    this.updateTotals(item);
                    this.dirMap['left']();
                    e.stop();
                }
            }.bind(this));
        }.bind(this));
        $$('input[type=text]').each(function (item) {
            if (item.value === '0') {
                item.value = 'M';
            }
            if (item.value === '10' && item.nextSibling.get('html') == 'True') {
                item.value = 'X';
            }
            this.updateTotals(item);
        }.bind(this));
        $$('input[type=submit]').addEvent('keydown', function (e) {
            if (e.key == 'up') {
                var inputs = $$('td input');
                inputs[inputs.length - 1].focus();
            }
        });
        $$('.retiring input[type=checkbox]').addEvent('change', function (e) {
            if (this.checked) {
                $(this).getParent('tr').getChildren('td input[type=text]').each(function (input) {
                    input.set('disabled', 'disabled');
                });
                $(this).getParent('tr').addClass('disabled');
            } else {
                $(this).getParent('tr').getChildren('td input[type=text]').each(function (input) {
                    input.set('disabled', '');
                });
                $(this).getParent('tr').removeClass('disabled');
            }
        });
        $$('.retiring input[type=checkbox]').fireEvent('change');
        $$('form').addEvent('submit', function (e) {
            $$('input[disabled]').set('disabled', '');
        });
    },

    updateTotals: function (input) {
        if (!input) {
            input = $$('.active input')[0];
        }
        var row = input.getParent('tr');
        var inputs = row.getElements('input[type=text]');
        var ET1 = 0;
        var ET2 = 0;
        var hits = 0;
        var golds = 0;
        var xs = 0;
        var rt = parseInt(row.getElement('.rt').get('rel'));
        if (isNaN(rt)) {
            rt = 0;
        }
        inputs.each(function (item, index) {
            var value = item.get('value');
            if (value == 'M' || value == '') {
                return;
            }
            if (value == 'X') {
                xs += 1;
                value = 10;
            }
            value = parseInt(value);
            if (index < 6) {
                ET1 += value;
            } else {
                ET2 += value;
            }
            hits += 1;
            if (value == 10) {
                golds += 1;
            }
        });
        var values = {
            'et1': ET1,
            'et2': ET2,
            'doz-total': ET1 + ET2,
            'hits': hits,
            'golds': golds,
            'xs': xs,
            'rt': rt + ET1 + ET2,
        };
        row.getElements('th').each(function (item, index) {
            Object.each(values, function (value, cls) {
                if (item.hasClass(cls)) {
                    item.set('html', value);
                }
            });
        });
    },

    move: function (dir) {
        var currentFocus = $$('input:focus')[0];
        if (!currentFocus) {
            return;
        }
        var row = currentFocus.getParent('tr');
        if (dir === 'up' || dir === 'down') {
            var table = row.getParent('table');
            var currentCell = row.getChildren().indexOf(currentFocus.getParent('td'));
            var inputs = table.getElements('td:nth-child(' + (currentCell + 1).toString() + ') input');
            var current = inputs.indexOf(currentFocus);
            if (dir === 'down') {
                if (inputs[current + 1]) {
                    inputs[current + 1].focus();
                } else {
                    $$('input[type=submit]')[0].focus();
                }
            }
            if (dir === 'up' && inputs[current - 1]) {
                inputs[current - 1].focus();
            }
        }
        if (dir === 'left' || dir === 'right') {
            var inputs = row.getElements('td input')
            var current = inputs.indexOf(currentFocus);
            if (dir === 'right' && inputs[current + 1]) {
                inputs[current + 1].focus();
            }
            if (dir === 'left' && inputs[current - 1]) {
                inputs[current - 1].focus();
            }
        }
    },

});
