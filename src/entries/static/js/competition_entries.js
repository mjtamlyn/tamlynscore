var Option = new Class({
    initialize: function (name, rel) {
        attrs = {
            html: name,
            'class': 'option',
            rel: rel,
        }
        el = new Element('li', attrs);
        return el
    }
});

var SelectWidget = new Class({

    initialize: function (widget) {
        this.widget = widget;
        this.parseOptions(widget.getElement('select'));
        this.input = widget.getElement('input');
        this.options = new Element('ul', {'class': 'options'});
        this.widget.adopt(this.options);
        this.addInputEvents();
        //this.options.adopt(new Option('New Archer', 'new'));
    },

    parseOptions: function (select) {
        this.resultsLookup = {};
        this.search = {};
        this.hits = {};
        select.getElements('option').each(function (option) {
            var object, value;
            value = option.get('value');
            if (value) {
                this.hits[value] = 0;
                object = JSON.decode(option.get('html'));
                object.name.split(' ').each(function (part) {
                    if (this.search[part]) {
                        this.search[part].push(value);
                    } else {
                        this.search[part] = [value];
                    }
                }.bind(this));
                this.resultsLookup[value] = object;
            }
        }.bind(this));
    },

    addInputEvents: function () {
        widget = this;
        widget.input.addEvent('keyup', function (e) {
            if (e.key == 'enter' || e.key == 'up' || e.key == 'down') {
                e.stop();
                return;
            }
            widget.options.empty();
            if (!this.value) {
                widget.options.setStyle('display', 'none');
                return;
            }
            var params = this.value.split(' ');
            var searchList = Object.keys(widget.search);
            Object.keys(widget.hits).each(function (item) {
                widget.hits[item] = 0;
            });
            params.each(function (param) {
                if (param === '') {
                    params.pop(param);
                    return;
                }
                searchList.each(function (searchTerm) {
                    if (RegExp('^' + param, 'i').test(searchTerm)) {
                        widget.search[searchTerm].each(function (i) {
                            widget.hits[i] += 1;
                        });
                    }
                });
            });
            widget.results = [];
            widget.displayResults = [];
            Object.keys(widget.hits).each(function (item) {
                if (widget.hits[item] === params.length) {
                    widget.results.push(widget.resultsLookup[item]);
                    widget.displayResults.push(new Option(widget.resultsLookup[item].name, item));
                }
            });
            widget.options.adopt(widget.displayResults, new Option('New Archer', 'new'));
            widget.options.setStyle('display', 'block');
            widget.options.getChildren().removeClass('selected');
            widget.options.firstChild.addClass('selected');
        });
    }

});
