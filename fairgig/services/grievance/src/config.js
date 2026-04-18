require('dotenv').config();

module.exports = {
    port: Number(process.env.GRIEVANCE_SERVICE_PORT || 8004),
    frontendOrigin: process.env.FRONTEND_ORIGIN || 'http://localhost:5173',
    jwtSecret: process.env.JWT_SECRET || 'change_me',
    rateLimitApiPerMinute: Number(process.env.RATE_LIMIT_API_PER_MINUTE || 100),
    db: {
        host: process.env.POSTGRES_HOST || 'localhost',
        port: Number(process.env.POSTGRES_PORT || 5432),
        database: process.env.POSTGRES_DB || 'fairgig',
        username: process.env.POSTGRES_USER || 'fairgig_admin',
        password: process.env.POSTGRES_PASSWORD || 'password'
    }
};
