const express = require('express');
const cors = require('cors');
const morgan = require('morgan');
const config = require('./config');
const sequelize = require('./db/connection');
require('./db/models');

const { apiLimiter } = require('./middleware/rateLimiter');
const complaintsRoutes = require('./routes/complaints');
const clustersRoutes = require('./routes/clusters');
const communityRoutes = require('./routes/community');

const app = express();

app.use(cors({ origin: config.frontendOrigin, credentials: true }));
app.use(express.json({ limit: '1mb' }));
app.use(morgan('dev'));
app.use(apiLimiter);

app.get('/health', (_req, res) => {
    res.json({ status: 'ok', service: 'grievance' });
});

app.use(complaintsRoutes);
app.use(clustersRoutes);
app.use(communityRoutes);

app.use((err, _req, res, _next) => {
    console.error(err);
    res.status(500).json({ detail: 'Internal server error', type: 'server_error', status: 500 });
});

async function start() {
    try {
        await sequelize.authenticate();
        app.listen(config.port, () => {
            console.log(`Grievance service running on :${config.port}`);
        });
    } catch (error) {
        console.error('Failed to start grievance service', error);
        process.exit(1);
    }
}

if (require.main === module) {
    start();
}

module.exports = app;
