const { DataTypes } = require('sequelize');
const sequelize = require('../connection');

const Complaint = sequelize.define(
    'Complaint',
    {
        id: { type: DataTypes.UUID, defaultValue: DataTypes.UUIDV4, primaryKey: true },
        worker_id: { type: DataTypes.UUID, allowNull: false },
        platform: { type: DataTypes.STRING(50), allowNull: false },
        category: { type: DataTypes.STRING(50), allowNull: false },
        title: { type: DataTypes.STRING(200), allowNull: false },
        description: { type: DataTypes.TEXT, allowNull: false },
        status: { type: DataTypes.STRING(20), allowNull: false, defaultValue: 'open' },
        tags: { type: DataTypes.ARRAY(DataTypes.TEXT), allowNull: false, defaultValue: [] },
        cluster_id: { type: DataTypes.UUID, allowNull: true },
        advocate_note: { type: DataTypes.TEXT, allowNull: true },
        escalated_by: { type: DataTypes.UUID, allowNull: true },
        escalated_at: { type: DataTypes.DATE, allowNull: true },
        resolved_at: { type: DataTypes.DATE, allowNull: true },
        is_public: { type: DataTypes.BOOLEAN, defaultValue: true },
        anonymous_display_id: { type: DataTypes.STRING(10), allowNull: true },
        upvotes: { type: DataTypes.INTEGER, defaultValue: 0 }
    },
    {
        tableName: 'complaints',
        schema: 'grievance',
        timestamps: true,
        underscored: true,
        createdAt: 'created_at',
        updatedAt: 'updated_at'
    }
);

Complaint.beforeCreate((complaint) => {
    if (!complaint.anonymous_display_id) {
        complaint.anonymous_display_id = `WKR-${Math.floor(1000 + Math.random() * 9000)}`;
    }
});

module.exports = Complaint;
