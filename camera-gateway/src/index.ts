import express, { NextFunction, Request, Response } from 'express';
import cors from 'cors';
import helmet from 'helmet';
import http from 'http';
import { config } from './config';
import { logger } from './logger';
import { connectDatabase, disconnectDatabase } from './prismaClient';
import healthRouter from './routes/health';
import streamsRouter from './routes/streams';
import camerasRouter from './routes/cameras';
import diagnosticsRouter from './routes/diagnostics';
import { streamManager } from './services/streamManager';

async function bootstrap(): Promise<void> {
  await connectDatabase();

  const app = express();
  const server = http.createServer(app);

  app.use(helmet());
  app.use(cors());
  app.use(express.json());
  app.use(express.urlencoded({ extended: true }));

  app.use((req, _res, next) => {
    logger.info({ method: req.method, url: req.url }, 'Incoming request');
    next();
  });

  app.use('/api', healthRouter);
  app.use('/api', camerasRouter);
  app.use('/api', diagnosticsRouter);
  app.use('/', streamsRouter);

  app.use((_req, res) => {
    res.status(404).json({ error: 'Not found' });
  });

  app.use((err: Error, _req: Request, res: Response, _next: NextFunction) => {
    logger.error({ err }, 'Unhandled error');
    res.status(500).json({ error: 'Internal server error' });
  });

  server.listen(config.port, () => {
    logger.info({ port: config.port }, 'Camera gateway listening');
  });

  const shutdown = async (signal: string) => {
    logger.info({ signal }, 'Shutting down camera gateway');
    server.close(() => {
      logger.info('HTTP server closed');
    });
    streamManager.stopAll();
    await disconnectDatabase();
    process.exit(0);
  };

  process.on('SIGINT', () => shutdown('SIGINT'));
  process.on('SIGTERM', () => shutdown('SIGTERM'));
}

bootstrap().catch((error) => {
  logger.error({ err: error }, 'Failed to bootstrap camera gateway');
  process.exit(1);
});




