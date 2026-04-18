const express = require('express');
const { body, query, validationResult } = require('express-validator');
const { Op } = require('sequelize');
const auth = require('../middleware/auth');
const requireRole = require('../middleware/roleGuard');
const { Complaint } = require('../db/models');
const { similarity } = require('../utils/similarity');

const router = express.Router();

const allowedPlatforms = [
    'Careem', 'Bykea', 'inDrive', 'Foodpanda', 'Cheetay', 'Daraz', 'Rozee',
    'Freelance_Upwork', 'Freelance_Fiverr', 'Freelance_Other', 'Domestic', 'Other'
];
const allowedCategories = [
    'commission_rate_change', 'account_deactivation', 'payment_delay',
    'incorrect_calculation', 'unsafe_working_condition', 'no_transparency', 'other'
];

function checkValidation(req, res, next) {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
        return res.status(400).json({ detail: 'Validation failed', type: 'validation_error', status: 400, errors: errors.array() });
    }
    return next();
}

router.post(
    '/complaints',
    auth,
    requireRole('worker', 'advocate', 'admin'),
    body('platform').isIn(allowedPlatforms),
    body('category').isIn(allowedCategories),
    body('title').isString().isLength({ min: 1, max: 200 }),
    body('description').isString().isLength({ min: 1, max: 2000 }),
    checkValidation,
    async (req, res) => {
        const complaint = await Complaint.create({
            worker_id: req.user.id,
            platform: req.body.platform,
            category: req.body.category,
            title: req.body.title,
            description: req.body.description,
            is_public: req.body.is_public !== false
        });
        return res.status(201).json(complaint);
    }
);

router.get('/complaints', auth, async (req, res) => {
    const page = Math.max(Number(req.query.page || 1), 1);
    const perPage = Math.min(Math.max(Number(req.query.per_page || 20), 1), 100);

    const where = {};
    if (req.query.platform) where.platform = req.query.platform;
    if (req.query.category) where.category = req.query.category;
    if (req.query.status) where.status = req.query.status;
    if (req.query.cluster_id) where.cluster_id = req.query.cluster_id;

    if (req.user.role === 'worker') {
        where[Op.or] = [{ is_public: true }, { worker_id: req.user.id }];
    }

    const { rows, count } = await Complaint.findAndCountAll({
        where,
        order: [['created_at', 'DESC']],
        offset: (page - 1) * perPage,
        limit: perPage
    });

    return res.json({ items: rows, page, per_page: perPage, total: count });
});

router.get('/complaints/:id', auth, async (req, res) => {
    const complaint = await Complaint.findByPk(req.params.id);
    if (!complaint) return res.status(404).json({ detail: 'Complaint not found', type: 'not_found', status: 404 });

    if (req.user.role === 'worker' && !complaint.is_public && complaint.worker_id !== req.user.id) {
        return res.status(403).json({ detail: 'Insufficient permissions', type: 'forbidden', status: 403 });
    }
    return res.json(complaint);
});

router.patch('/complaints/:id/status', auth, requireRole('advocate', 'admin'), async (req, res) => {
    const complaint = await Complaint.findByPk(req.params.id);
    if (!complaint) return res.status(404).json({ detail: 'Complaint not found', type: 'not_found', status: 404 });

    complaint.status = req.body.status || complaint.status;
    complaint.advocate_note = req.body.advocate_note || complaint.advocate_note;
    await complaint.save();
    return res.json(complaint);
});

router.post('/complaints/:id/tags', auth, requireRole('advocate', 'admin'), async (req, res) => {
    const complaint = await Complaint.findByPk(req.params.id);
    if (!complaint) return res.status(404).json({ detail: 'Complaint not found', type: 'not_found', status: 404 });
    complaint.tags = Array.isArray(req.body.tags) ? req.body.tags : [];
    await complaint.save();
    return res.json(complaint);
});

router.post('/complaints/:id/cluster', auth, requireRole('advocate', 'admin'), async (req, res) => {
    const complaint = await Complaint.findByPk(req.params.id);
    if (!complaint) return res.status(404).json({ detail: 'Complaint not found', type: 'not_found', status: 404 });
    complaint.cluster_id = req.body.cluster_id || null;
    await complaint.save();
    return res.json(complaint);
});

router.get('/complaints/:id/similar', auth, async (req, res) => {
    const complaint = await Complaint.findByPk(req.params.id);
    if (!complaint) return res.status(404).json({ detail: 'Complaint not found', type: 'not_found', status: 404 });

    const pool = await Complaint.findAll({
        where: {
            id: { [Op.ne]: complaint.id },
            platform: complaint.platform
        },
        limit: 50
    });

    const baseText = `${complaint.title} ${complaint.description}`;
    const ranked = pool
        .map((c) => ({ item: c, score: similarity(baseText, `${c.title} ${c.description}`) }))
        .filter((x) => x.score > 0)
        .sort((a, b) => b.score - a.score)
        .slice(0, 5)
        .map((x) => ({ ...x.item.toJSON(), similarity: Number(x.score.toFixed(2)) }));

    return res.json({ items: ranked });
});

module.exports = router;
