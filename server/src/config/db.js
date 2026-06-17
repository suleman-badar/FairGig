import mongoose from 'mongoose';
import dotenv from 'dotenv';

dotenv.config();

const connectDB = async () => {
    try {
        await mongoose.connect(process.env.MONGO_URI);
        console.log("COnnection successfull");
    } catch (err) {
        console.log("Error in connecting to database", err.message);
        process.exit(1);
    }
};

export default connectDB;
