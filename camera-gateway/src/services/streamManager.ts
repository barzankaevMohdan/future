import { spawn, ChildProcess } from 'child_process';
import { Response } from 'express';
import { config } from '../config';
import { logger } from '../logger';
import { buildRtspUrl, buildSafeRtspUrl, getCameraById } from './cameraService';

interface StreamContext {
  cameraId: number;
  ffmpeg?: ChildProcess;
  clients: Set<Response>;
  restartTimestamps: number[];
  stopTimer?: NodeJS.Timeout;
}

class StreamManager {
  private streams = new Map<number, StreamContext>();

  public async attachClient(cameraId: number, res: Response): Promise<void> {
    const camera = await getCameraById(cameraId);
    if (!camera || !camera.isActive) {
      res.status(404).json({ error: 'Camera not found or inactive' });
      return;
    }
    if (!camera.recognitionEnabled) {
      res.status(403).json({ error: 'Streaming disabled for this camera' });
      return;
    }

    const safeUrl = buildSafeRtspUrl(camera);
    logger.info({ cameraId, url: safeUrl }, 'Client subscribed to camera stream');

    const context = this.getOrCreateContext(cameraId);
    context.clients.add(res);

    if (!context.ffmpeg) {
      this.startFfmpeg(context, camera);
    }

    res.on('close', () => {
      context.clients.delete(res);
      this.scheduleShutdown(context);
    });
  }

  private getOrCreateContext(cameraId: number): StreamContext {
    if (!this.streams.has(cameraId)) {
      this.streams.set(cameraId, {
        cameraId,
        clients: new Set(),
        restartTimestamps: [],
      });
    }
    return this.streams.get(cameraId)!;
  }

  private startFfmpeg(context: StreamContext, camera: Awaited<ReturnType<typeof getCameraById>>): void {
    if (!camera) return;

    if (!this.canRestart(context)) {
      logger.error({ cameraId: context.cameraId }, 'Restart limit reached, not starting ffmpeg');
      this.closeAllClients(context, 'Restart limit reached');
      return;
    }

    const rtspUrl = buildRtspUrl(camera);
    const safeUrl = buildSafeRtspUrl(camera);
    logger.info({ cameraId: context.cameraId, url: safeUrl }, 'Starting ffmpeg process');

    const args = [
      '-rtsp_transport', 'tcp',
      '-i', rtspUrl,
      '-vf', 'scale=1280:720',
      '-f', 'mpjpeg',
      '-boundary_tag', 'frame',
      '-q:v', '5',
      '-r', '10',
      '-'
    ];

    const ffmpeg = spawn(config.ffmpegPath, args, { stdio: ['ignore', 'pipe', 'pipe'] });
    context.ffmpeg = ffmpeg;
    this.recordRestart(context);

    ffmpeg.stdout.on('data', (chunk) => {
      context.clients.forEach((client) => {
        if (!client.destroyed) {
          client.write(chunk);
        }
      });
    });

    ffmpeg.stderr.on('data', (data) => {
      const message = data.toString();
      if (message.toLowerCase().includes('error')) {
        logger.warn({ cameraId: context.cameraId, message }, 'FFmpeg stderr');
      }
    });

    ffmpeg.on('exit', (code, signal) => {
      logger.warn({ cameraId: context.cameraId, code, signal }, 'FFmpeg exited');
      context.ffmpeg = undefined;
      this.closeAllClients(context, 'Stream stopped');
    });

    ffmpeg.on('error', (error) => {
      logger.error({ cameraId: context.cameraId, err: error }, 'FFmpeg error');
      context.ffmpeg = undefined;
      this.closeAllClients(context, 'Stream failed');
    });
  }

  private scheduleShutdown(context: StreamContext): void {
    if (context.clients.size > 0 || context.stopTimer) {
      return;
    }
    context.stopTimer = setTimeout(() => {
      if (context.clients.size === 0) {
        this.stopStream(context.cameraId);
      }
    }, config.streamIdleTimeoutMs);
  }

  public stopStream(cameraId: number): void {
    const context = this.streams.get(cameraId);
    if (!context) return;

    logger.info({ cameraId }, 'Stopping stream');
    if (context.stopTimer) {
      clearTimeout(context.stopTimer);
      context.stopTimer = undefined;
    }

    if (context.ffmpeg && !context.ffmpeg.killed) {
      context.ffmpeg.kill('SIGTERM');
    }

    this.closeAllClients(context, 'Stream stopped');
    this.streams.delete(cameraId);
  }

  public stopAll(): void {
    this.streams.forEach((_context, cameraId) => this.stopStream(cameraId));
    this.streams.clear();
  }

  private closeAllClients(context: StreamContext, reason: string): void {
    context.clients.forEach((client) => {
      if (!client.destroyed) {
        client.end();
      }
    });
    context.clients.clear();
    logger.info({ cameraId: context.cameraId, reason }, 'Clients closed');
  }

  private recordRestart(context: StreamContext): void {
    context.restartTimestamps.push(Date.now());
    const windowStart = Date.now() - config.restartWindowMs;
    context.restartTimestamps = context.restartTimestamps.filter((ts) => ts >= windowStart);
  }

  private canRestart(context: StreamContext): boolean {
    const windowStart = Date.now() - config.restartWindowMs;
    context.restartTimestamps = context.restartTimestamps.filter((ts) => ts >= windowStart);
    return context.restartTimestamps.length < config.maxRestartsPerWindow;
  }
}

export const streamManager = new StreamManager();

