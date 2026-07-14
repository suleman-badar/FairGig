import prisma from "../libs/prisma.js";

async function main() {
  // ---------- Users ----------
  const worker = await prisma.user.upsert({
    where: { email: "admin@example.com" },
    update: {
      name: "Admin",
      username : "admin",
      role: "worker"
    },
    create: {
      name: "Admin",
      username: "admin",
      email: "admin@example.com",
      passwordHash: "admin",
      role: "worker",
    },
  });

  const verifier = await prisma.user.upsert({
    where: { email: "ali@example.com" },
    update: {},
    create: {
      name: "Ali",
      username: "ali",
      email: "ali@example.com",
      passwordHash: "hashed_password_2",
      role: "verifier",
    },
  });

  await prisma.user.upsert({
    where: { email: "ahmed@example.com" },
    update: {},
    create: {
      name: "Ahmed",
      username: "ahmed",
      email: "ahmed@example.com",
      passwordHash: "hashed_password_3",
      role: "analyst",
    },
  });

  // ---------- Earnings ----------
  const earning1 = await prisma.earning.create({
    data: {
      workerId: worker.id,
      amount: 2500,
      platform: "foodpanda",
      hoursWorked: 8,
      deductions: 100,
    },
  });

  const earning2 = await prisma.earning.create({
    data: {
      workerId: worker.id,
      amount: 1800,
      platform: "indrive",
      hoursWorked: 6,
      deductions: 50,
    },
  });

  // ---------- Verifications ----------
  await prisma.verification.createMany({
    data: [
      {
        earningId: earning1.id,
        verifierId: verifier.id,
        status: "approved",
        submissionProof: "receipt_foodpanda_001.jpg",
        comment: "Everything looks correct.",
      },
      {
        earningId: earning2.id,
        verifierId: verifier.id,
        status: "pending",
        submissionProof: "receipt_indrive_001.jpg",
        comment: null,
      },
    ],
  });

  console.log("✅ Database seeded successfully!");
}

main()
  .catch((e) => {
    console.error(e);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });