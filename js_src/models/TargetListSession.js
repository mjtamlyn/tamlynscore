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
        this.boss = null;
        this.target = null;
        this.allocation = null;
    }
}

class TargetListSession {
    constructor({ sessionTime, archersPerBoss, targetList }) {
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
    }
}

export default TargetListSession;
