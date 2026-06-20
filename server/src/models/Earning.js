import mongoose from 'mongoose';

const earningSchema = new mongoose.Schema({
    worker_id: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'User',
    },
    amount: {
        type: Number,
        required: true
    },
    date:{
        type: Date,
        default: Date.now
    },
    platform:{
        type: String,
        enum: ['foodpanda', 'indrive', 'yango', 'other'],
        default: 'Other',
        required: true
    },
    hours_worked:{
        type: Number,
        required: true
    },
    deductions:{
        type: Number,
        default: 0
    },
    created_at: {
        type: Date,
        default: Date.now
    }
});


export default mongoose.model('Earning',earningSchema); 