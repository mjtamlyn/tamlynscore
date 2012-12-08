(function ($) {
    _.templateSettings = {
        interpolate : /\{\{(.+?)\}\}/g
    };

    var Club = Backbone.Model.extend({});

    var ClubView = Backbone.View.extend({
        className: 'club',
        render: function () {
            var context = this.get_context();
            this.$el.html(_.template(this.template, context));
            this.$el.attr('class', this.className + ' position-' + context.position);
        },
        get_context: function () {
            var context = _.clone(this.model.attributes);
            context.team_1 = this.model.attributes.team[0].name;
            context.team_1_score = this.model.attributes.team[0].score;
            context.team_2 = this.model.attributes.team[1].name;
            context.team_2_score = this.model.attributes.team[1].score;
            context.team_3 = this.model.attributes.team[2].name;
            context.team_3_score = this.model.attributes.team[2].score;
            return context
        },
    });

    window.init = function (data, template) {
        var clubs = [];
        _.each(data, function (club_data) {
            var club = new Club(club_data);
            clubs.push(club);
            var view = new ClubView({'model': club});
            club.view = view;
            view.template = template;
            view.render();
            $('#leaderboard').append(view.el);
        });

        $('#update').click(function () {
            $.get(window.location.href, {}, function (data) {
                data = JSON.parse(data);
                _.each(clubs, function (club) {
                    updated = (_.detect(data, function (club_data) {
                        return (club.id === club_data.id) && club_data;
                    }));
                    club.set(updated);
                    club.view.render();
                });
            });
        });
    }
})($);
