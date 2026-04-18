const express = require('express');
const auth = require('../middleware/auth');
const requireRole = require('../middleware/roleGuard');
const { Cluster, Complaint } = require('../db/models');

const router = express.Router();

router.post('/clusters', auth, requireRole('advocate', 'admin'), async (req, res) => {
    const cluster = await Cluster.create({
        label: req.body.label,
        description: req.body.description,
        platform: req.body.platform,
        created_by: req.user.id
    });
    return res.status(201).json(cluster);
});

router.get('/clusters', auth, requireRole('advocate', 'admin'), async (_req, res) => {
    const clusters = await Cluster.findAll({ order: [['created_at', 'DESC']] });
    return res.json({ items: clusters });
});

router.get('/clusters/:id', auth, requireRole('advocate', 'admin'), async (req, res) => {
    const cluster = await Cluster.findByPk(req.params.id);
    if (!cluster) return res.status(404).json({ detail: 'Cluster not found', type: 'not_found', status: 404 });
    const complaints = await Complaint.findAll({ where: { cluster_id: cluster.id }, order: [['created_at', 'DESC']] });
    return res.json({ cluster, complaints });
});

router.patch('/clusters/:id/status', auth, requireRole('advocate', 'admin'), async (req, res) => {
    const cluster = await Cluster.findByPk(req.params.id);
    if (!cluster) return res.status(404).json({ detail: 'Cluster not found', type: 'not_found', status: 404 });
    cluster.status = req.body.status || cluster.status;
    await cluster.save();
    return res.json(cluster);
});

module.exports = router;
