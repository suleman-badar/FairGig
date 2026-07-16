import AppError from "../utils/appError.js";

export const validate = (schema) => (req, res, next) => {
    const result = schema.safeParse(req.body);

    if (!result.success) {
        return next(
            new AppError(
                result.error.issues.map(issue => issue.message).join(", "),
                400
            )
        );
    }

    // Replace req.body with the validated data
    req.body = result.data;

    next();
};