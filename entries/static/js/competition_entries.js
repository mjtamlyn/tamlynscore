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

    Implements: Options,

    options: {
        callback: function () {},
        blank: 'New...'
    },

    initialize: function (options) {
        this.setOptions(options);
        this.initOptions = this.options;
        this.widget = this.initOptions.widget;
        this.selectElement = this.widget.getElement('select');
        this.parseOptions(this.selectElement);
        this.input = this.widget.getElement('input');
        this.options = this.widget.getElement('.options');
        this.addInputEvents();
        this.callback = this.initOptions.callback;
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
        var widget = this;
        var showOptions = function (e) {
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
                if (widget.hits[item] >= params.length) {
                    widget.results.push(widget.resultsLookup[item]);
                    widget.displayResults.push(new Option(widget.resultsLookup[item].name, item));
                }
            });
            widget.options.adopt(widget.displayResults, new Option(widget.initOptions.blank, 'new'));
            widget.options.setStyle('display', 'block');
            widget.options.getChildren().removeClass('selected');
            widget.options.firstChild.addClass('selected');
        };
        widget.input.addEvent('keydown', function (e) {
            if (e.key == 'enter' || e.key == 'up' || e.key == 'down') {
                if (e.key == 'up' && this.value) {
                    widget.moveUp();
                }
                if (e.key == 'down' && this.value) {
                    widget.moveDown();
                }
                if (e.key == 'enter' && this.value) {
                    this.blur()
                }
                e.stop();
            }
        });
        widget.input.addEvent('keyup', showOptions);
        widget.input.addEvent('focus', showOptions);
        widget.input.addEvent('blur', function () {
            if (widget.input.get('value')) {
                widget.select();
            }
        });
    },

    moveUp: function () {
        var current = this.options.getElement('.selected');
        if (current.previousSibling) {
            current.removeClass('selected');
            current.previousSibling.addClass('selected');
        }
    },

    moveDown: function () {
        var current = this.options.getElement('.selected');
        if (current.nextSibling) {
            current.removeClass('selected');
            current.nextSibling.addClass('selected');
        }
    },

    select: function () {
        this.options.setStyle('display', 'none');
        var current = this.options.getElement('.selected');
        var rel = current.get('rel');
        this.selectedObject;
        this.is_new = (rel === 'new');
        if (this.is_new) {
            this.selectedObject = {id: ''}
        } else {
            this.selectedObject = this.resultsLookup[rel];
        }
        var option = this.selectElement.getElement('option[value=' + this.selectedObject.id + ']')
        option.set('selected', 'selected');
        if (!this.is_new) {
            this.input.set('value', this.selectedObject.name);
        }
        this.callback(this);
    },

    setValue: function (value) {
        this.selectedObject = this.resultsLookup[value];
        this.input.set('value', this.selectedObject.name);
        var option = this.selectElement.getElement('option[value=' + this.selectedObject.id + ']')
        option.set('selected', 'selected');
    },

    reset: function () {
        this.input.set('value', '');
        this.selectElement.getElement('option[value=]').set('selected', 'selected');
    }

});

var ButtonWidget = new Class({

    initialize: function (widget) {
        this.widget = widget
        widget.getElements('.button').addEvent('click', function () {
            if (!this.hasClass('selected')) {
                widget.getElements('.button').removeClass('selected');
            };
            this.toggleClass('selected');
            var value = this.get('rel');
            if (!this.hasClass('selected')) {
                value = '';
            }
            widget.getElement('option[value=' + value + ']').set('selected', 'selected');
        });
    },

    reset: function () {
        this.widget.getElements('.button').removeClass('selected');
        this.widget.getElement('option[value=]').set('selected', 'selected');
    },

    setValue: function (value) {
        this.widget.getElement('[rel=' + value + ']').fireEvent('click');
    }

});
