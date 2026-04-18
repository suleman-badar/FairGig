const { DataTypes } = require('sequelize');
const sequelize = require('../connection');

const Cluster = sequelize.define(
    'Cluster',
    {
        id: { type: DataTypes.UUID, defaultValue: DataTypes.UUIDV4, primaryKey: true },
        label: { type: DataTypes.STRING(200), allowNull: false },
        description: { type: DataTypes.TEXT, allowNull: true },
        platform: { type: DataTypes.STRING(50), allowNull: true },
        created_by: { type: DataTypes.UUID, allowNull: false },
        complaint_count: { type: DataTypes.INTEGER, defaultValue: 0 },
        status: { type: DataTypes.STRING(20), defaultValue: 'active' }
    },
    {
        tableName: 'clusters',
        schema: 'grievance',
        timestamps: true,
        underscored: true,
        createdAt: 'created_at',
        updatedAt: 'updated_at'
    }
);

module.exports = Cluster;
