gc, lc, gr, lr = OlympicSessionRound.objects.all()

gr.make_matches(level=6, start=1, half_only=True)
gr.make_matches(level=5, start=1)
gr.make_matches(level=4, start=1)
gr.make_matches(level=3, start=1, expanded=True)
gr.make_matches(level=2, start=9, expanded=True)
gr.make_matches(level=1, start=9, expanded=True)

lr.make_matches(level=4, start=9)
lr.make_matches(level=3, start=9, expanded=True)
lr.make_matches(level=2, start=13, expanded=True)
lr.make_matches(level=1, start=13, expanded=True)

gc.make_matches(level=5, start=17)
gc.make_matches(level=4, start=17)
gc.make_matches(level=3, start=17, expanded=True)
gc.make_matches(level=2, start=17, expanded=True)
gc.make_matches(level=1, start=17, expanded=True)

lc.make_matches(level=4, start=25)
lc.make_matches(level=3, start=25, expanded=True)
lc.make_matches(level=2, start=21, expanded=True)
lc.make_matches(level=1, start=21, expanded=True)

quit()
