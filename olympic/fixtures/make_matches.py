from olympic.models import OlympicSessionRound


# BUCS 2014
gr, lr, l, b, c = OlympicSessionRound.objects.all()[16:]

gr.match_set.all().delete()
lr.match_set.all().delete()
b.match_set.all().delete()
l.match_set.all().delete()
c.match_set.all().delete()

gr.make_matches(level=7, start=7, timing=1)
gr.make_matches(level=6, start=39, timing=2)
gr.make_matches(level=5, start=41, timing=3)
gr.make_matches(level=4, start=33, timing=4)
gr.make_matches(level=3, start=21, timing=5)
gr.make_matches(level=2, start=21, timing=6, expanded=True)
gr.make_matches(level=1, start=21, timing=7, expanded=True)

lr.make_matches(level=6, start=7, timing=2)
lr.make_matches(level=5, start=25, timing=3)
lr.make_matches(level=4, start=25, timing=4)
lr.make_matches(level=3, start=17, timing=5)
lr.make_matches(level=2, start=17, timing=6, expanded=True)
lr.make_matches(level=1, start=17, timing=7, expanded=True)

b.make_matches(level=5, start=9, timing=3)
b.make_matches(level=4, start=17, timing=4)
b.make_matches(level=3, start=13, timing=5)
b.make_matches(level=2, start=13, timing=6, expanded=True)
b.make_matches(level=1, start=13, timing=7, expanded=True)

l.make_matches(level=4, start=9, timing=4)
l.make_matches(level=3, start=9, timing=5)
l.make_matches(level=2, start=9, timing=6, expanded=True)
l.make_matches(level=1, start=9, timing=7, expanded=True)

c.make_matches(level=4, start=1, timing=4)
c.make_matches(level=3, start=5, timing=5)
c.make_matches(level=2, start=5, timing=6, expanded=True)
c.make_matches(level=1, start=5, timing=7, expanded=True)
