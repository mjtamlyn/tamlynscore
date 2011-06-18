var ValuesManager = new Class({

    setUp: function () {
        $$('input')[0].focus();
        $$('input').each(function (item, index, array) {
            if (item.get('type') !== 'text') {
                return;
            }
            item.addEvent('keydown', function (e) {
                var validCodes = {
                    '48': '10',
                '49': '1',
                '50': '2',
                '51': '3',
                '52': '4',
                    '53': '5',
                    '54': '6',
                    '55': '7',
                    '56': '8',
                    '57': '9',
                    '189': 'X',
                    '192': 'M',
                }
                if (e.code in validCodes) {
                    item.set('value', validCodes[e.code]);
                    if (array[index + 1]) {
                        array[index + 1].focus();
                    }
                    this.updateTotals(item);
                    e.stop();
                }
            }.bind(this));
        }.bind(this));
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
    }

});
