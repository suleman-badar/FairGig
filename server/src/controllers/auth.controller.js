import { register,login,refresh } from '../services/auth.service.js';


const registerUser = async (req, res) => {
    const { confirmPassword, ...userData } = req.body; // Exclude confirmPassword from userData
   const user = await register(userData);
   res.status(201).json({
    success: true,
    message: "User registered successfully",
    data: user
   });
};

const loginUser = async (req, res) => {
    const auth = await login(req.body);

    res.cookie("refreshToken", auth.refreshToken, {
        httpOnly: true,
        secure: process.env.NODE_ENV === "production",
        sameSite: "strict",
        maxAge: 7 * 24 * 60 * 60 * 1000, // 7 days
    });

    res.status(200).json({
        success: true,
        message: "User logged in successfully",
        data: {
            user: auth.user,
            accessToken: auth.accessToken,
        }
    });
}


const refreshToken = async (req, res) => {
    const refreshToken = req.cookies.refreshToken;
    const newAccessToken = await refresh(refreshToken);

    res.status(200).json({
        success: true,
        message: "Access token refreshed successfully",
        data: {
            accessToken: newAccessToken,
        }
    });

}


export { registerUser, loginUser, refreshToken };