const textMatcher = (terms, target) => {
    if (!terms) {
        return true;
    }
    const parts = terms.split(' ');
    if (parts.length === 1) {
        return new RegExp(terms, 'i').test(target);
    }
    return true;
};

export default textMatcher;
