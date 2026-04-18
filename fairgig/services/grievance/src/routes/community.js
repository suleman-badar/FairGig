const express = require('express');
const { Complaint } = require('../db/models');

const router = express.Router();

router.get('/community', async (req, res) => {
    const page = Math.max(Number(req.query.page || 1), 1);
    const perPage = Math.min(Math.max(Number(req.query.per_page || 20), 1), 100);

    const where = { is_public: true };
    if (req.query.platform) where.platform = req.query.platform;
    if (req.query.category) where.category = req.query.category;

    const { rows, count } = await Complaint.findAndCountAll({
        where,
        order: [['created_at', 'DESC']],
        offset: (page - 1) * perPage,
        limit: perPage
    });

    const items = rows.map((c) => ({
        id: c.id,
        anonymous_display_id: c.anonymous_display_id,
        platform: c.platform,
        category: c.category,
        title: c.title,
        description: c.description,
        status: c.status,
        tags: c.tags,
        cluster_id: c.cluster_id,
        created_at: c.created_at
    }));

    return res.json({ items, page, per_page: perPage, total: count });
});

module.exports = router;
