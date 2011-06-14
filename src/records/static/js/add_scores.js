var SmartInput = new Class({
    setUp: function () {
        $$('.smart-input').each(function (item, index, array) {
            var input, select, search;
            input = item.getElement('input[type=text]');
            select = item.getElement('select');
            search = {};
            select.getElements('option').each(function (option) {
                var name, value;
                value = option.get('value');
                if (value) {
                    name = option.get('html'); 
                    name.split(' ').each(function (part) {
                        if (search[part]) {
                            search[part].push(value);
                        } else {
                            search[part] = [value];
                        }
                    });
                }
            });
            input.addEvent('keyup', function (e) {
                if (e.key == 'enter' || e.key == 'up' || e.key == 'down') {
                    console.log('hello');
                    e.stop();
                }
                var params = this.value.split(' ');
                var searchList = Object.keys(search);
            });
        });
    },
});
