import { PrismaClient } from '@prisma/client';
import { logger } from './logger';

export const prisma = new PrismaClient({
  log: [
    { level: 'error', emit: 'event' },
    { level: 'warn', emit: 'event' },
  ],
});

prisma.$on('error', (event) => {
  logger.error({ err: event }, 'Prisma error');
});

prisma.$on('warn', (event) => {
  logger.warn({ warn: event }, 'Prisma warning');
});

export async function connectDatabase(): Promise<void> {
  await prisma.$connect();
  logger.info('Camera gateway connected to database');
}

export async function disconnectDatabase(): Promise<void> {
  await prisma.$disconnect();
  logger.info('Camera gateway disconnected from database');
}




