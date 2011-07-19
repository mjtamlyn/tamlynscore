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
    },

    updateTotals: function (input) {
        var row = input.getParent('tr');
        var inputs = row.getElements('input');
        var ET1 = 0;
        var ET2 = 0;
        var hits = 0;
        var golds = 0;
        var xs = 0;
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
        var values = [ET1, ET2, ET1 + ET2, hits, golds, xs];
        row.getElements('th').each(function (item, index) {
            item.set('html', values[index]);
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
