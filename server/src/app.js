import express from "express"
import prisma from "./libs/prisma.js";

const app = express();

app.get("/", async (req, res) => {
    res.send("Welcome");
});

app.post("/register", async (req, res) => {
    const { name, email, password } = req.body;
    const user = await prisma.user.create({
        data: {
            name,
            email,
            password
        }
    });
    delete user.password; // Remove password from the response for security reasons
    res.json(user);
});

app.get("/users", async (req, res) => {
    const users = await prisma.user.findMany();
    users.forEach(user => delete user.password); // Remove password from each user object for security reasons
    res.json(users);
});

export default app;
