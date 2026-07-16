import { Router } from "express";
import { registerUser, loginUser, refreshToken } from "../controllers/auth.controller.js";
import asyncHandler from "../middlewares/asyncHandler.js";
import { validate } from "../validations/validate.js";
import { registerSchema } from "../validations/auth.validation.js";

const router = Router();
//REGISTER
router.get("/register", (req, res) => {
    res.send("Register page");
});
router.post("/register", validate(registerSchema), asyncHandler(registerUser));

// TODO: ADD THEM LATER

// router.put("/register", asyncHandler(updateUser));
// router.delete("/register", asyncHandler(deleteUser));

//LOGIN
router.get("/login", (req, res) => {
    res.send("Login page");
});
router.post("/login", validate(loginSchema), asyncHandler(loginUser));
router.post("/logout", asyncHandler(logoutUser));

router.get("/refresh", asyncHandler(refreshToken));


export default router;