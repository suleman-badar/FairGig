const jwt = require('jsonwebtoken');
const config = require('../config');

function auth(req, res, next) {
    const header = req.headers.authorization || '';
    const token = header.startsWith('Bearer ') ? header.slice(7) : null;
    if (!token) {
        return res.status(401).json({ detail: 'Missing token', type: 'auth_error', status: 401 });
    }

    try {
        const payload = jwt.verify(token, config.jwtSecret);
        req.user = { id: payload.sub, role: payload.role };
        return next();
    } catch (err) {
        return res.status(401).json({ detail: 'Invalid token', type: 'auth_error', status: 401 });
    }
}

module.exports = auth;
