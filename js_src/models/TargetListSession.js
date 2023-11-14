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
        this.session.store.action('DELETE', {id: this.id});
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
        this.session.store.action('SET', {id: this.id, value: { boss, target }});
    }
}

class TargetListSession {
    constructor({ id, sessionTime, archersPerBoss, targetList, unallocatedEntries }) {
        this.id = id,
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
                    categories: archer.categories,
                    boss: boss.number,
                    target: target,
                    allocation: `${boss.number}${target}`,
                    searchtext: archer.searchtext,
                    session: this,
                });
                lookup[target] = instance;
                this.archers.push(instance);
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
                categories: archer.categories,
                boss: null,
                target: null,
                allocation: null,
                searchtext: archer.searchtext,
                session: this,
            });
            this.unallocatedEntries.push(instance);
            this.archers.push(archer);
        });
    }

    addBoss(lettersUsed) {
        const lastBossNumber = this.bosses.length ? this.bosses[this.bosses.length - 1].number : 0;
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

    insertBossAfter(number, lettersUsed) {
        const index = this.bosses.findIndex(boss => boss.number === number);
        const lookup = {};
        lettersUsed.forEach(letter => {
            lookup[letter] = null;
        });
        this.bosses.forEach(boss => {
            if (boss.number > number) {
                boss.number++;
            }
        });
        this.archers.forEach(archer => {
            if (archer.boss && archer.boss > number) {
                archer.boss++;
                archer.allocation = `${archer.boss}${archer.target}`;
            }
        });
        this.bosses.splice(index + 1, 0, {
            number: number + 1,
            lookup: lookup,
        });
        this.store.action('SHIFTUP', {session: this.id, number});
    }

    removeBoss(number) {
        const index = this.bosses.findIndex(boss => boss.number === number);
        this.bosses.splice(index, 1);
        this.bosses.forEach(boss => {
            if (boss.number > number) {
                boss.number--;
            }
        });
        this.archers.forEach(archer => {
            if (archer.boss && archer.boss > number) {
                archer.boss--;
                archer.allocation = `${archer.boss}${archer.target}`;
            }
        });
        this.store.action('SHIFTDOWN', {session: this.id, number});
    }
}

export default TargetListSession;
