(function () {
    $(document).ready(function () {

        var setPresent = function (row) {
            row.toggleClass('present');
        };

        $('.present').click(function (e) {
            var $el = $(this);
            var request = $.post(
                '',
                {
                    present: true,
                    pk: $el.attr('data-pk'),
                },
                function (response) {
                    setPresent($el.closest('tr'));
                }
            );
        });

        $('.not-present').click(function (e) {
            var $el = $(this);
            var request = $.post(
                '',
                {
                    present: false,
                    pk: $el.attr('data-pk'),
                },
                function (response) {
                    setPresent($el.closest('tr'));
                }
            );
        });

        $('.registration-board').each(function (index, board) {
            var clubs = {};
            board = $(board);
            board.find('table tr.archer').each(function (i, allocation) {
                allocation = $(allocation);
                var club_id = allocation.attr('data-club');
                if (!club_id) { return; }
                var club_name = allocation.attr('data-clubname');
                if (!(club_name in clubs)) {
                    clubs[club_name] = {'id': club_id, 'archers': [], 'name': club_name};
                }
                clubs[club_name]['archers'].push(allocation);
            });
            var filter = board.find('.actions .club-filter');
            $.each(clubs, function (key, club) {
                filter.append($('<option>').attr('data-club', club.name).html(club.name.replace('<', '---').replace('>', '---')));
            });
            filter.change(function () {
                var club = this.value;
                board.find('table tr.archer.hidden').removeClass('hidden');
                if (club === '--All--') {
                    return;
                } else {
                    board.find('table tr.archer:not([data-clubname="'+club+'"])').addClass('hidden');
                }
            });
        });

    });
})();
