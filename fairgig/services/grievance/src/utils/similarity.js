function similarity(text1, text2) {
    const words1 = new Set((text1 || '').toLowerCase().split(/\W+/).filter((w) => w.length > 3));
    const words2 = new Set((text2 || '').toLowerCase().split(/\W+/).filter((w) => w.length > 3));
    if (words1.size === 0 || words2.size === 0) return 0;
    const intersection = [...words1].filter((w) => words2.has(w));
    return intersection.length / Math.max(words1.size, words2.size);
}

module.exports = { similarity };
