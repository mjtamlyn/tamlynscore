import Score from './Score';

class Store {
    constructor({ api, scores }) {
        this.scores = scores.map(score => new Score({ store: this, ...score }));
        this.api = api;
    }

    save() {
        const data = JSON.stringify({
            scores: this.scores.map(score => score.serialize()),
        });
        fetch(this.api, {
            method: 'POST',
            credentials: 'same-origin',
            body: data,
        }).then((response) => {
            console.log(response.status);
        });;
    }
}

export default Store;
