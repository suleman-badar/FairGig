/*
  Warnings:

  - You are about to drop the column `updatedAt` on the `RefreshToken` table. All the data in the column will be lost.
  - A unique constraint covering the columns `[jti]` on the table `RefreshToken` will be added. If there are existing duplicate values, this will fail.
  - Added the required column `jti` to the `RefreshToken` table without a default value. This is not possible if the table is not empty.
  - Added the required column `lastUsedAt` to the `RefreshToken` table without a default value. This is not possible if the table is not empty.

*/
-- AlterTable
ALTER TABLE "RefreshToken" DROP COLUMN "updatedAt",
ADD COLUMN     "jti" TEXT NOT NULL,
ADD COLUMN     "lastUsedAt" TIMESTAMP(3) NOT NULL;

-- CreateIndex
CREATE UNIQUE INDEX "RefreshToken_jti_key" ON "RefreshToken"("jti");
