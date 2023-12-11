def competition(competition, is_admin=False):
    return {
        'name': competition.full_name,
        'short': competition.short_name,
        'url': competition.get_absolute_url(),
        'hasNovices': competition.has_novices,
        'hasAges': competition.has_agb_age_groups or competition.has_juniors,
        'isAdmin': is_admin,
    }


def round_shot(round_shot, session):
    return {
        'name': round_shot.name,
        'totalArrows': round_shot.arrows,
        'endLength': session.arrows_entered_per_end,
        'endCount': round_shot.arrows / session.arrows_entered_per_end,
        'splits': round_shot.splits,
        'resultsOptions': {
            'scoringHeadings': round_shot.score_sheet_headings,
            'hasXs': round_shot.has_xs,
            'hasHits': round_shot.has_hits,
            'gold9s': round_shot.gold_9s,
        },
    }


def score(competition, entry, score):
    categories = {
        'bowstyle': entry.bowstyle.name,
        'gender': entry.archer.get_gender_display(),
    }
    if competition.has_novices and entry.novice == 'N':
        categories['novice'] = entry.get_novice_display()
    if competition.has_juniors and entry.age == 'J':
        categories['age'] = entry.get_age_display()
    if competition.has_agb_age_groups and entry.agb_age:
        categories['age'] = entry.get_agb_age_display()
    return {
        'id': score.id,
        'target': score.target.label,
        'boss': score.target.boss,
        'name': entry.archer.name,
        'categories': categories,
        'arrows': [a.json_value for a in score.arrow_set.order_by('arrow_of_round')],
    }
