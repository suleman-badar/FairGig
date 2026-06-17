import AppError from "../utils/AppError.js";

const errorHandler = (err, req, res, next) => {
    console.log("Error in error handler", err);

    // Create a copy of the error object to avoid mutating the original error
    let error = { ...err };
    error.message = err.message;

    // Set default status code to 500 if not already set
    let statusCode = err.statusCode || 500;

    if (err.name === "CastError") {
        error = new AppError("Invalid ID format", 400);
        statusCode = 400;
    }

    if(err.code===11000){
        error = new AppError("Duplicate Field value entered", 400);
        statusCode= 400;
    }

    // Handle Mongoose validation errors and send a user friendly(much readable) msg to client
    if ( err.name === "ValidationError"){
        const msg= Object.values(err.errors).map((val)=>val.message).join(", ");
        error = new AppError(msg, 400);
        statusCode= 400;
    }

    // Send the error response to the client in json format
    res.status(statusCode).json({
        success:false,
        message : error.message || "Internal Server Error",
        stack: process.env.NODE_ENV === "development" ? error.stack : undefined,
    });
};

export default errorHandler;


