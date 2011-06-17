var SmartInput = new Class({
    setUp: function () {
        $$('.smart-input').each(function (item, index, array) {
            var input, select, search, hits, resultsLookup;
            input = item.getElement('input[type=text]');
            select = item.getElement('select');
            search = {};
            hits = {};
            resultsLookup = {};
            select.getElements('option').each(function (option) {
                var archer, value;
                value = option.get('value');
                if (value) {
                    hits[value] = 0;
                    archer = JSON.decode(option.get('html'));
                    archer.name.split(' ').each(function (part) {
                        if (search[part]) {
                            search[part].push(value);
                        } else {
                            search[part] = [value];
                        }
                    });
                    resultsLookup[value] = archer;
                }
            });
            input.addEvent('keyup', function (e) {
                if (e.key == 'enter' || e.key == 'up' || e.key == 'down') {
                    console.log('hello');
                    e.stop();
                    return;
                }
                $('archer-options').empty();
                if (!this.value) {
                    return;
                }
                var params = this.value.split(' ');
                var searchList = Object.keys(search);
                Object.keys(hits).each(function (item) {
                    hits[item] = 0;
                });
                params.each(function (param) {
                    if (param === '') {
                        params.pop(param);
                        return;
                    }
                    searchList.each(function (searchTerm) {
                        if (RegExp('^' + param, 'i').test(searchTerm)) {
                            search[searchTerm].each(function (i) {
                                hits[i] += 1;
                            });
                        }
                    });
                });
                var results = [];
                var displayResults = [];
                Object.keys(hits).each(function (item) {
                    if (hits[item] === params.length) {
                        results.push(resultsLookup[item]);
                        displayResults.push(new Element('p', {
                            html: resultsLookup[item].name,
                            'class': 'archer-select',
                        }));
                    }
                });
                $('archer-options').adopt(displayResults);
                $('archer-options').firstChild.addClass('selected');
            });
        });
    },
});
