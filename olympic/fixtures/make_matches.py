from olympic.models import OlympicSessionRound
# OA 2011
#gc, lc, gr, lr = OlympicSessionRound.objects.all()
#
#gr.make_matches(level=6, start=1, half_only=True)
#gr.make_matches(level=5, start=1)
#gr.make_matches(level=4, start=1)
#gr.make_matches(level=3, start=1, expanded=True)
#gr.make_matches(level=2, start=9, expanded=True)
#gr.make_matches(level=1, start=9, expanded=True)
#
#lr.make_matches(level=4, start=9)
#lr.make_matches(level=3, start=9, expanded=True)
#lr.make_matches(level=2, start=13, expanded=True)
#lr.make_matches(level=1, start=13, expanded=True)
#
#gc.make_matches(level=5, start=17)
#gc.make_matches(level=4, start=17)
#gc.make_matches(level=3, start=17, expanded=True)
#gc.make_matches(level=2, start=17, expanded=True)
#gc.make_matches(level=1, start=17, expanded=True)
#
#lc.make_matches(level=4, start=25)
#lc.make_matches(level=3, start=25, expanded=True)
#lc.make_matches(level=2, start=21, expanded=True)
#lc.make_matches(level=1, start=21, expanded=True)

# OA 2012
gr, lr, gc, lc = OlympicSessionRound.objects.all()[4:]

gr.match_set.all().delete()
lr.match_set.all().delete()
gc.match_set.all().delete()
lc.match_set.all().delete()

gr.make_matches(level=7, start=1, quarter_only=True)
gr.make_matches(level=6, start=1)
gr.make_matches(level=5, start=1)
gr.make_matches(level=4, start=17)
gr.make_matches(level=3, start=25)
gr.make_matches(level=2, start=25, expanded=True)
gr.make_matches(level=1, start=25, expanded=True)

lr.make_matches(level=6, start=17, half_only=True)
lr.make_matches(level=5, start=17)
lr.make_matches(level=4, start=25)
lr.make_matches(level=3, start=29)
lr.make_matches(level=2, start=29, expanded=True)
lr.make_matches(level=1, start=29, expanded=True)

gc.make_matches(level=6, start=33, half_only=True)
gc.make_matches(level=5, start=33)
gc.make_matches(level=4, start=33)
gc.make_matches(level=3, start=33)
gc.make_matches(level=2, start=33, expanded=True)
gc.make_matches(level=1, start=33, expanded=True)

lc.make_matches(level=5, start=33)
lc.make_matches(level=4, start=41)
lc.make_matches(level=3, start=37)
lc.make_matches(level=2, start=37, expanded=True)
lc.make_matches(level=1, start=37, expanded=True)

quit()
