var SmartInput = new Class({

    results: [],
    displayResults: [],
    newArcher: new Element('p', {
        html: 'New archer',
        'class': 'archer-select new-archer',
        rel: 'new',
    }),

    setUp: function () {
        var smartInput = this;
        $$('.smart-input').each(function (item, index, array) {
            var input, select, search, hits;
            input = item.getElement('input[type=text]');
            select = item.getElement('select');
            search = {};
            hits = {};
            smartInput.resultsLookup = {};
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
                    smartInput.resultsLookup[value] = archer;
                }
            });
            input.addEvent('keydown', function (e) {
                if (e.key == 'enter' || e.key == 'up' || e.key == 'down') {
                    if (e.key == 'up' && this.value) {
                        smartInput.moveUp();
                    }
                    if (e.key == 'down' && this.value) {
                        smartInput.moveDown();
                    }
                    if (e.key == 'enter' && this.value) {
                        smartInput.selectArcher(this);
                    }
                    e.stop();
                }
            });
            input.addEvent('keyup', function (e) {
                if (e.key == 'enter' || e.key == 'up' || e.key == 'down') {
                    e.stop();
                    return;
                }
                $('archer-options').empty();
                if (!this.value) {
                    $$('.new-archer-options').addClass('hidden');
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
                smartInput.results = [];
                smartInput.displayResults = [];
                Object.keys(hits).each(function (item) {
                    if (hits[item] === params.length) {
                        smartInput.results.push(smartInput.resultsLookup[item]);
                        smartInput.displayResults.push(new Element('p', {
                            html: smartInput.resultsLookup[item].name,
                            'class': 'archer-select',
                            rel: item,
                        }));
                    }
                });
                $('archer-options').adopt(smartInput.displayResults, smartInput.newArcher);
                $$('#archer-options .archer-select').removeClass('selected');
                $('archer-options').firstChild.addClass('selected');
            });
        });
    },

    moveUp: function () {
        var current = $$('.archer-select.selected')[0];
        if (current.previousSibling) {
            current.removeClass('selected');
            current.previousSibling.addClass('selected');
        }
    },

    moveDown: function () {
        var current = $$('.archer-select.selected')[0];
        if (current.nextSibling) {
            current.removeClass('selected');
            current.nextSibling.addClass('selected');
        }
    },

    selectArcher: function (input) {
        input.blur();
        $$('.new-archer-options').addClass('hidden');
        var current = $$('.archer-select.selected')[0];
        var rel = current.get('rel');
        if (rel == 'new') {
            $$('.new-archer-options').removeClass('hidden');
            $('id_new_archer').set('checked', 'checked');
            $('id_bowstyle').getElement('option').set('selected', 'selected');
            $('id_club').getElement('option').set('selected', 'selected');
        } else {
            $$('.archer-options').removeClass('hidden');
            var archer = this.resultsLookup[rel];
            $$('#id_bowstyle option[value=' + archer.bowstyle + ']').set('selected', 'selected');
            $$('#id_club option[value=' + archer.club + ']').set('selected', 'selected');
            $('id_new_archer').set('checked', '');
            $('archer_input').set('value', archer.name);
        }
        $('archer-options').empty();
    },
});
