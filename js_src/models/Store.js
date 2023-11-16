class Store {
    constructor({ api, data, autoSaveEnabled = true, dataName = 'data' }) {
        this.data = data;
        this.data.forEach(item => item.store = this);
        this.dataName = dataName
        this.api = api;
        this.dirty = false;
        this.loading = false;
        this.hooks = {
            dirty: [],
            loading: [],
        };
        this.autoSave = null;
        this.autoSaveEnabled = autoSaveEnabled;
        this.retry = null;
        this.retryCount = 0;
    }

    registerDirty(hook) {
        this.hooks.dirty.push(hook);
    }
    unregisterDirty(hook) {
        if (this.hooks.dirty.includes(hook)) {
            this.hooks.dirty.splice(this.hooks.dirty.indexOf(hook), 1);
        }
    }

    registerLoading(hook) {
        this.hooks.loading.push(hook);
    }
    unregisterLoading(hook) {
        if (this.hooks.loading.includes(hook)) {
            this.hooks.loading.splice(this.hooks.loading.indexOf(hook), 1);
        }
    }

    setDirty() {
        this.dirty = true;
        this.hooks.dirty.forEach(hook => hook(true));
        if (this.autoSaveEnabled) {
            if (this.autoSave) {
                clearTimeout(this.autoSave);
            }
            this.autoSave = setTimeout(() => this.save(), 1000 * 10);
        }
    }

    _sendRequest(data, retry) {
        if (this.retry) {
            clearTimeout(this.retry);
            this.retry = null;
        }
        if (!this.dirty) {
            return;
        }

        this.loading = true;
        this.dirty = false;
        this.hooks.loading.forEach(hook => hook(true));
        this.hooks.dirty.forEach(hook => hook(false));
        fetch(this.api, {
            method: 'POST',
            credentials: 'same-origin',
            body: JSON.stringify(data),
        }).then((response) => {
            this.retryCount = 0;
            this.loading = false;
            this.hooks.loading.forEach(hook => hook(false));
            if (response.status !== 200) {
                this.dirty = true;
                this.hooks.dirty.forEach(hook => hook(true));
                throw('Something else went wrong?');
            }
        }).catch(() => {
            this.loading = false;
            this.dirty = true;
            this.hooks.loading.forEach(hook => hook(false));
            this.hooks.dirty.forEach(hook => hook(true));
            this.retryCount++;
            this.retry = setTimeout(() => retry, 1000 * this.retryCount);
        });
    }

    save() {
        const data = {};
        data[this.dataName] = this.data.map(item => item.serialize())
        this._sendRequest(data, this.save);
    }
}

export default Store;
