def competition(competition, is_admin=False):
    return {
        'name': competition.full_name,
        'short': competition.short_name,
        'url': competition.get_absolute_url(),
        'hasNovices': competition.has_novices,
        'hasAges': competition.has_agb_age_groups or competition.has_juniors,
        'isAdmin': is_admin,
    }


def round_shot(session_round, session):
    round_shot = session_round.shot_round
    return {
        'name': round_shot.name,
        'totalArrows': round_shot.arrows,
        'endLength': session.arrows_entered_per_end,
        'endCount': round_shot.arrows / session.arrows_entered_per_end,
        'splits': round_shot.splits,
        'resultsOptions': {
            'scoringHeadings': session_round.score_sheet_headings,
            'hasXs': session_round.has_xs,
            'xsAre10s': session_round.xs_are_10s,
            'hasHits': session_round.has_hits,
            'hasGolds': session_round.has_golds,
            'hasElevens': session_round.has_elevens,
            'gold9s': session_round.gold_9s,
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
