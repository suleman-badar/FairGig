import mongoose from 'mongoose';

const verificationSchema = new mongoose.Schema({
    earning_id: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'Earning',
        required: true
    },
    verifier_id: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'User',
        required: true
    },

    /* i can either use rejected status here and send 
       a corrent msg or maybe use a new enum needs_correction
       and send msg to the worker to correct the submission */
    status: {
        type: String,
        enum: ['pending', 'approved', 'rejected'], 
        default: 'pending'
    },
    submission_proof: {
        required: true
    },
    comment: {
        type: String,
    },
    created_at: {
        type: Date,
        default: Date.now
    },

});


export default mongoose.model('Verification', verificationSchema);