import jwt from "jsonwebtoken";

export function generateAccessToken(user) {
    return jwt.sign(
        {
            sub: user.id,
            email: user.email,
        },
        process.env.JWT_ACCESS_SECRET,
        {
            expiresIn: process.env.JWT_ACCESS_EXPIRES_IN,
        }
    );
}

export function generateRefreshToken(user,jti) {
    return jwt.sign(
        {
            sub: user.id,
            jti, 
        },
        process.env.JWT_REFRESH_SECRET,
        {
            expiresIn: process.env.JWT_REFRESH_EXPIRES_IN,
        }
    );
}