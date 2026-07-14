import app from "./app.js"
import connectDB from "./libs/prisma.js"
import dns from "node:dns/promises";
dns.setServers(["1.1.1.1"]);

const port=8080;

app.listen(port,  ()=>{
    console.log(`Server started on port: ${port}`);
    connectDB();
});

// console.log("File is running succcessfiully");



