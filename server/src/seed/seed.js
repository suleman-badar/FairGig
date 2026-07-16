import prisma from "../libs/prisma.js";
import bcrypt from "bcrypt";

async function main() {
  const passwordHash = await bcrypt.hash("password123", 10);

  // --------------------
  // Users
  // --------------------

  const admin = await prisma.user.upsert({
    where: { email: "admin@fairgig.com" },
    update: {
      name: "Admin",
      role: "admin",
    },
    create: {
      name: "Admin",
      email: "admin@fairgig.com",
      passwordHash,
      role: "admin",
    },
  });

  const worker = await prisma.user.upsert({
    where: { email: "worker@fairgig.com" },
    update: {},
    create: {
      name: "Worker",
      email: "worker@fairgig.com",
      passwordHash,
      role: "worker",
    },
  });

  const verifier = await prisma.user.upsert({
    where: { email: "verifier@fairgig.com" },
    update: {},
    create: {
      name: "Verifier",
      email: "verifier@fairgig.com",
      passwordHash,
      role: "verifier",
    },
  });

  const analyst = await prisma.user.upsert({
    where: { email: "analyst@fairgig.com" },
    update: {},
    create: {
      name: "Analyst",
      email: "analyst@fairgig.com",
      passwordHash,
      role: "analyst",
    },
  });

  // --------------------
  // Earnings
  // --------------------

  const earning1 = await prisma.earning.create({
    data: {
      workerId: worker.id,
      amount: 3500,
      platform: "foodpanda",
      hoursWorked: 8,
      deductions: 100,
    },
  });

  const earning2 = await prisma.earning.create({
    data: {
      workerId: worker.id,
      amount: 2400,
      platform: "indrive",
      hoursWorked: 6,
      deductions: 50,
    },
  });

  // --------------------
  // Verifications
  // --------------------

  await prisma.verification.createMany({
    data: [
      {
        earningId: earning1.id,
        verifierId: verifier.id,
        status: "approved",
        submissionProof: "foodpanda_receipt.jpg",
        comment: "Verified successfully.",
      },
      {
        earningId: earning2.id,
        verifierId: verifier.id,
        status: "pending",
        submissionProof: "indrive_receipt.jpg",
        comment: null,
      },
    ],
  });

  // --------------------
  // Role Request
  // --------------------

  await prisma.roleRequest.create({
    data: {
      userId: worker.id,
      requestedRole: "verifier",
      status: "pending",
    },
  });

  console.log("✅ Database seeded successfully.");
}

main()
  .catch((err) => {
    console.error(err);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });