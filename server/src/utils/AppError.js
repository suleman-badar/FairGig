class AppError extends Error {
    constructor(message, statusCode) {
        super(message) // Call the parent class constructor

        this.statusCode = statusCode;

        /*     This flag tells your app:
         👉 “This is a known, expected error”
         Examples of operational errors:
         -User not found
         -Invalid password
         -Validation error
         -Unauthorized access
         NOT operational errors:
         -database crash
         -syntax bug
         -memory failure */
        this.isOperational = true;

        /* This method creates a stack trace for the error,
           which is useful for debugging.It captures the
           current state of the call stack at the point 
           where the error was created and it excludes the 
           constructor function itself from the stack trace. */
        Error.captureStackTrace(this, this.constructor); 
    }
}

export default AppError;