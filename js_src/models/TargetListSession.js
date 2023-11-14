class SessionEntry {
    constructor({ id, name, club, categories, boss, target, allocation, searchtext, session }) {
        this.id = id;
        this.name = name;
        this.club = club;
        this.categories = categories;
        this.boss = boss;
        this.target = target;
        this.allocation = allocation;
        this.searchtext = searchtext;
        this.session = session;
    }

    deleteAllocation() {
        this.session.store.setDirty();
        this.session.store.delete({id: this.id});
        delete this.session.bosses.find(boss => boss.number === this.boss).lookup[this.target];
        this.session.unallocatedEntries.push(this);
        this.boss = null;
        this.target = null;
        this.allocation = null;
    }

    setAllocation({ boss, target }) {
        this.boss = boss;
        this.target = target;
        this.allocation = `${boss}${target}`;
        this.session.bosses.find(boss => boss.number === this.boss).lookup[this.target] = this;
        this.session.unallocatedEntries = this.session.unallocatedEntries.filter(entry => entry.id !== this.id);
        this.session.store.setDirty();
        this.session.store.set({id: this.id, value: { boss, target }});
    }
}

class TargetListSession {
    constructor({ sessionTime, archersPerBoss, targetList, unallocatedEntries }) {
        this.sessionTime = sessionTime;
        this.archersPerBoss = archersPerBoss;
        this.archers = []
        this.bosses = targetList.map(boss => {
            const lookup = {};
            for (const [target, archer] of Object.entries(boss.archers)) {
                if (!archer) {
                    lookup[target] = null;
                    continue;
                }
                const instance = new SessionEntry({
                    id: archer.id,
                    name: archer.name,
                    club: archer.club,
                    categories: {
                        bowstyle: archer.bowstyle,
                        novice: archer.novice,
                        age: archer.age,
                        gender: archer.gender,
                    },
                    boss: boss.number,
                    target: target,
                    allocation: `${boss.number}${target}`,
                    searchtext: archer.text,
                    session: this,
                });
                lookup[target] = instance;
                this.archers.push(archer);
            }

            return {
                number: boss.number,
                lookup: lookup,
            };
        });
        this.unallocatedEntries = [];
        unallocatedEntries.forEach(archer => {
            const instance = new SessionEntry({
                id: archer.id,
                name: archer.name,
                club: archer.club,
                categories: {
                    bowstyle: archer.bowstyle,
                    novice: archer.novice,
                    age: archer.age,
                    gender: archer.gender,
                },
                boss: null,
                target: null,
                allocation: null,
                searchtext: archer.text,
                session: this,
            });
            this.unallocatedEntries.push(instance);
            this.archers.push(archer);
        });
    }

    addBoss(lettersUsed) {
        const lastBossNumber = this.bosses[this.bosses.length - 1].number;
        const lookup = {};
        lettersUsed.forEach(letter => {
            lookup[letter] = null;
        });
        this.bosses.push({
            number: lastBossNumber + 1,
            lookup: lookup,
        });
    }

    addStartBoss(lettersUsed) {
        const firstBossNumber = this.bosses[0].number;
        const lookup = {};
        lettersUsed.forEach(letter => {
            lookup[letter] = null;
        });
        this.bosses = [{
            number: firstBossNumber - 1,
            lookup: lookup,
        }, ...this.bosses];
    }
}

export default TargetListSession;
