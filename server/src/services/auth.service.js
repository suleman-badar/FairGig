import { prisma } from "../utils/prisma.js";
import bcrypt from "bcrypt";
import AppError from "../utils/appError.js";
import { generateAccessToken, generateRefreshToken } from "../utils/jwt.js";
import crypto from "crypto";
import jwt from "jsonwebtoken";

const SALT_ROUNDS =
    Number(process.env.BCRYPT_SALT_ROUNDS) || 12;

const REFRESH_TOKEN_EXPIRY_MS =
    Number(process.env.JWT_REFRESH_EXPIRY) * 1000;

async function saveRefreshToken(
    userId,
    jti,
    refreshToken,
    expiresAt,
    db = prisma
) {

    const refreshTokenHash = await bcrypt.hash(
        refreshToken,
        SALT_ROUNDS
    );

    await db.refreshToken.create({
        data: {
            userId,
            jti,
            tokenHash: refreshTokenHash,
            expiresAt,
        },
    });
}

async function issueTokens(user) {
    const accessToken = generateAccessToken(user);

    const jti = crypto.randomUUID();
    const refreshToken = generateRefreshToken(user, jti);

    return {
        accessToken,
        refreshToken,
        jti,
        expiresAt: new Date(
            Date.now() + REFRESH_TOKEN_EXPIRY_MS
        ),
    };
}


export async function register(data) {
    const { name, email, password } = data;

    const existingUser = await prisma.user.findUnique({
        where: { email },
    });
    if (existingUser) {
        throw new AppError("User already exists.", 400);
    }

    const passwordHash = await bcrypt.hash(password, SALT_ROUNDS);

    const user = await prisma.user.create({
        data: {
            name,
            email,
            passwordHash,
        },
        select: {           //this tells prisma which fields to return after creating user
            id: true,
            name: true,
            email: true,
            role: true,
            createdAt: true,
        },
    });

    const tokens = await issueTokens(user);

    await saveRefreshToken(
        user.id,
        tokens.jti,
        tokens.refreshToken,
        tokens.expiresAt
    );

    return {
        user,
        accessToken: tokens.accessToken,
        refreshToken: tokens.refreshToken,
    };
}

export async function login(data) {
    const { email, password } = data;

    const user = await prisma.user.findUnique({
        where: { email },
        select: {
            id: true,
            name: true,
            email: true,
            passwordHash: true,
            role: true,
            createdAt: true,
        }
    });
    if (!user) {
        throw new AppError("Invalid email or password.", 401);
    }

    // if password is correct
    const isMatch = await bcrypt.compare(password, user.passwordHash);
    if (!isMatch) {
        throw new AppError("Invalid email or password.", 401);
    }

    const { passwordHash, ...userData } = user;
    const tokens = await issueTokens(userData);

    await saveRefreshToken(
        userData.id,
        tokens.jti,
        tokens.refreshToken,
        tokens.expiresAt
    );

    return {
        user: userData,
        accessToken: tokens.accessToken,
        refreshToken: tokens.refreshToken,
    };
}




export async function refresh(refreshToken) {
    if (!refreshToken) {
        throw new AppError("Refresh token is required.", 401);
    }
    //check if refresh token is valid
    let decoded;
    try {
        decoded = jwt.verify(refreshToken, process.env.JWT_REFRESH_SECRET);
    } catch (err) {
        throw new AppError("Invalid refresh token.", 401);
    }

    //extract jti and sub from decoded token
    const { sub, jti } = decoded;
    if (!sub || !jti) {
        throw new AppError("Invalid refresh token.", 401);
    }

    //find refresh token in database
    const storedToken = await prisma.refreshToken.findUnique({
        where: { jti },
    });
    if (!storedToken) {
        throw new AppError("Invalid refresh token.", 401);
    }

    //revoked or expired check
    if (storedToken.revokedAt) {
        throw new AppError("Refresh token has revoked.", 401);
    }
    if (storedToken.expiresAt < new Date()) {
        throw new AppError("Refresh token has expired.", 401);
    }


    //compare the provided refresh token with the stored hash
    const isMatch = await bcrypt.compare(refreshToken, storedToken.tokenHash);
    if (!isMatch) {
        throw new AppError("Invalid refresh token.", 401);
    }

    //find the user associated with the refresh token
    const user = await prisma.user.findFirst({
        where: {
            id: storedToken.userId,
            deletedAt: null, // Ensure that a deleted user cannot refresh their token
        },
        select: {
            id: true,
            name: true,
            email: true,
            role: true,
            createdAt: true,
        }
    });
    if (!user) {
        throw new AppError("User not found.", 404);
    }

    //geberate new jti and refresh token
    const tokens = await issueTokens(user);

    await prisma.$transaction(async (tx) => {
        const now = new Date();

        await tx.refreshToken.update({
            where: {
                id: storedToken.id,
            },
            data: {
                revokedAt: now,
                lastUsedAt: now,
            },
        });

        await saveRefreshToken(
            user.id,
            tokens.jti,
            tokens.refreshToken,
            tokens.expiresAt,
            tx
        );
    });

    return {
        accessToken: tokens.accessToken,
        refreshToken: tokens.refreshToken,
    };
};