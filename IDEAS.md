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








Model rewrite thoughts
======================

# Scoring system "rewrite"

## Modelling

### accounts
Need to add (good) user access

### core
SubRound - python config
Round - python config
Bowstyle - enum
Country - remove
Region - remove
County - remove
Club - ok
Archer - ok

### entries
Tournament - remove
Sponsor - python config
Competition - ok
ResultsMode - ok
Session - ok
SessionRound - ok
CompetitionEntry - ok
SessionEntry - ok
TargetAllocation - compress onto SessionEntry

### scores
Score - compress onto SessionEntry
Arrow - compress onto SessionEntry (using array of a custom PG type)
Dozen - compress onto SessionEntry

### olympic
OlympicRound - python config
Category - python config
OlympicSessionRound - ok
Seeding - ok
Match - ok
Result - ok

## Views/UI

Setup competition does not exist yet - it should do. The current admin process
is faffy and doesn't give a clear picture of what the competition looks like
after it's done.

The next step is to get entries set up for the tournament. There are two
primary methods - one is archer (or club) led entry, the other is TO led entry.
Both cases require two separate steps - firstly getting the individuals in the
system in their own right, and secondly filling in their entry details. When we
are doing TO led entry, it makes sense in some cases to also have the target
list allocation as part of the same process.

From a UI perspective it would be nice to have a representation of an archer
which is carried through this whole process. This would show clearly their
details (or the details of their entry when known) and should be used on the
front end throughout the process. If we get to the point they have images, we
can use those. It needs to have various sizes, but it's in theory a nice JS
widget which knows how to display itself in different ways depending on screen
size and user interaction. This also means we don't have to worry about what
information we're making accessible to each view - we just send it all. It may
lend itself to caching as well. Web component??

Registration needs to allow easily the ability to change the details, but
otherwise is quite straightforwards.

Score entry needs a few changes, mainly on the front end. It would be *really*
nice to have a more "live" user interface for this, and generally better
navigation. Also the UI needs unifying between different devices, and we need
mobile apps/websites which can handle it. Finally, we need better user access,
so we can set up users which can only access the scores for a particular
target.

Leaderboards can be made shinier, but the real changes are in how we program
them on the backend. I'd like to push more of the processing into the database,
store things using arrays and custom data types, and allow the database to do
most of the results calculation itself. It should then return a list of archers
(and/or club information) as ids, and we display those using the standard
representation.

H2H is its own kettle of fish. There's a huge amount of scope for good UI/UX
here, but we need personalised logins before we can do that easily. The
underlying logic is correct and the data model largely good so there's not too
much to change there.

## Architecture

I'd like to explore the architecture model where there are "views" which handle
sections of the page independantly, and the front end has a similar structure
as well. PJAXing is good too, but what I don't want to do is too much
templating/rendering on the front end. I'd like there to be "views" (widgets)
in the GUI sense which take data and return rendered HTML, and views in the
python sense which take requests and stitch these together appropriately
depending on how we've asked for them. This should mean that every page can be
rendered in a single response on a page refresh, but also that individual
secions can be modelled separately and the JS request them as appropriate. In
particular, this means when data is updated it's relatively simple to post it
using the JS and replace sections of the page.
