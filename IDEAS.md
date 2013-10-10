Ideas
=====

Where do we want to go with this project? I could potentially be much more than
just a simple scoring system. It's already quite complex - there are a lot of
ideas all mushed together in a single codebase and quite tightly coupled (like
lanyrd!). In fact, that's a good comparison - it's a lot more like a lanyrd
than a heroku - it's grown organically from some shoddy code to start with, and
isn't really well developed. It's lacking in tests, there are some poor design
decisions, who knows where the bugs are and large chunks were insufficiently
powerful to be useful the first time round.

So, what can we do to fix this? Well the first step is probably to write down
what the ideas for the project are - in an ideal world, what do we want this
(ecosystem of) site(s) to be able to do?

It's first purpose is to be able to successfully run a tournament. This should
cover everything you need from both a TO perspective and an archer's
perspective, and a Judge's perspective. It needs to be able to correctly
publish and fix in time results, store them usefully, maintain records of
events etc. Ideally, this would become powerful enough to be used by a huge
range of tournaments across the world - target, field, university,
international etc. The existing systems are not that high quality, so this is
potentially not a ridiculous proposition given enough work.

The second primary purpose is as a fully integrated, quality replacement for
archery scorepad/iarcher/rcherz/etc. It should provide a way for archers to
record their practice (scores, volume, sight marks, everything else), share
information with their friends (kit set up, PBs etc) and also integrate with
the tournament side. This side of the application is almost non existant at
present.

So, how do we go about achieving both of these goals, and what are the design
principles we want to follow on the way there?

Firstly, let's consider the main concepts we need to cover. The first and most
important is the Archer. We may have a huge amount of information about the
archer, or very very little. The second is the Score. This has a lot of
metadata - rounds, handicaps etc etc, but in it's simplest form it's a number
of points accrued. The next is the Competition - this is a key part of the
first primary goal.

So we can begin to separate out our data model into three primary components,
split along these lines. We have "people and organisations" - Archers, Clubs,
Users, TOs, Judges etc. We then have "score data" - rounds, distances, scores,
etc. Finally there are competitions - which have entries, session times, target
lists, results etc. There are obviously links here - results require scores
which require archers to have shot them, so these are coupled data models, but
it does allow the "archer mode" to sit separately from the "tournament mode".

Now let's start to think about the technologies we need to build this system.
We want a avoid a "monolithic" approach as much as we can I think - we will
probably need a central (normalized) data store, but the applications should
talk to this independantly and not be too tightly integrated. Some data which
is "rebuildable" should perhaps be stored with these separate applications. For
performance reasons though, there some merit to the web applications being
"Django" style apps - each with its own manage.py, settings etc. The central
data applications then provide a *python* API which the other components (Rest
API, web front ends etc) can interface with. Each component may have its own
data stores etc as needed.

In particular an interesting technological challenge for the tournaments
component is portability - it needs to be able to work away from the internet -
and you need to be able to pull down everything which that shoot needs to make
it work. I don't have an immediate answer to this right now.
