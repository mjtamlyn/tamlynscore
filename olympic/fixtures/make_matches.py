from olympic.models import OlympicSessionRound


# OA 2014
gr, lr, gc, lc = OlympicSessionRound.objects.all()[21:]

gr.match_set.all().delete()
lr.match_set.all().delete()
gc.match_set.all().delete()
lc.match_set.all().delete()

gr.make_matches(level=6, start=5, timing=1, half_only=True)
gr.make_matches(level=5, start=5, timing=2)
gr.make_matches(level=4, start=13, timing=4)
gr.make_matches(level=3, start=17, timing=5)
gr.make_matches(level=2, start=17, timing=6, expanded=True)
gr.make_matches(level=1, start=17, timing=7, expanded=True)

lr.make_matches(level=5, start=5, timing=3)
lr.make_matches(level=4, start=5, timing=4)
lr.make_matches(level=3, start=13, timing=5)
lr.make_matches(level=2, start=13, timing=6, expanded=True)
lr.make_matches(level=1, start=13, timing=7, expanded=True)

gc.make_matches(level=5, start=21, timing=3)
gc.make_matches(level=4, start=21, timing=4)
gc.make_matches(level=3, start=21, timing=5)
gc.make_matches(level=2, start=21, timing=6, expanded=True)
gc.make_matches(level=1, start=21, timing=7, expanded=True)

lc.make_matches(level=4, start=29, timing=4)
lc.make_matches(level=3, start=25, timing=5)
lc.make_matches(level=2, start=25, timing=6, expanded=True)
lc.make_matches(level=1, start=25, timing=7, expanded=True)
