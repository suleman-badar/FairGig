import express from "express"
import prisma from "./libs/prisma.js";
import cookieParser from "cookie-parser";
import cors from "cors";

const app = express();

app.get("/", async (req, res) => {
    res.send("Welcome");
});

app.use(express.json());
app.use(cookieParser());

app.use(cors({
    origin: "http://localhost:5173", // Replace with your frontend URL
    credentials: true,
    }
));

export default app;
