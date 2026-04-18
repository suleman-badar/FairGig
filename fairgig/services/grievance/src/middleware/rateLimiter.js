const rateLimit = require('express-rate-limit');
const config = require('../config');

const apiLimiter = rateLimit({
    windowMs: 60 * 1000,
    limit: config.rateLimitApiPerMinute,
    standardHeaders: true,
    legacyHeaders: false,
    message: { detail: 'Too many requests', type: 'rate_limit', status: 429 }
});

module.exports = { apiLimiter };
