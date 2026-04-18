const Complaint = require('./Complaint');
const Cluster = require('./Cluster');

Complaint.belongsTo(Cluster, { foreignKey: 'cluster_id', as: 'cluster' });
Cluster.hasMany(Complaint, { foreignKey: 'cluster_id', as: 'complaints' });

module.exports = { Complaint, Cluster };
