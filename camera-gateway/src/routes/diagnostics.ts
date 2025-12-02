import { Router } from 'express';
import { buildRtspUrl, buildSafeRtspUrl, getCameraById } from '../services/cameraService';
import { spawn } from 'child_process';
import { config } from '../config';
import { logger } from '../logger';

const router = Router();

router.post('/cameras/:id/preview', async (req, res, next) => {
  try {
    const cameraId = Number(req.params.id);
    if (!Number.isInteger(cameraId)) {
      res.status(400).json({ error: 'Invalid camera id' });
      return;
    }

    const camera = await getCameraById(cameraId);
    if (!camera) {
      res.status(404).json({ error: 'Camera not found' });
      return;
    }

    const rtspUrl = buildRtspUrl(camera);
    const safeUrl = buildSafeRtspUrl(camera);

    const result = await runPreviewProbe(rtspUrl);
    if (result.ok) {
      res.json({
        ok: true,
        cameraId,
        safeRtspUrl: safeUrl,
        durationMs: result.durationMs,
      });
    } else {
      res.status(502).json({
        ok: false,
        cameraId,
        safeRtspUrl: safeUrl,
        error: result.error,
      });
    }
  } catch (error) {
    next(error);
  }
});

function runPreviewProbe(rtspUrl: string): Promise<{ ok: true; durationMs: number } | { ok: false; error: string }> {
  return new Promise((resolve) => {
    const args = [
      '-rtsp_transport',
      'tcp',
      '-i',
      rtspUrl,
      '-frames:v',
      '1',
      '-f',
      'null',
      '-',
    ];

    const startedAt = Date.now();
    const ffmpeg = spawn(config.ffmpegPath, args);
    let stderr = '';

    ffmpeg.stderr.on('data', (chunk) => {
      stderr += chunk.toString();
    });

    ffmpeg.on('error', (error) => {
      logger.error({ err: error }, 'Preview ffmpeg failed to start');
      resolve({ ok: false, error: error.message });
    });

    ffmpeg.on('exit', (code) => {
      if (code === 0) {
        resolve({ ok: true, durationMs: Date.now() - startedAt });
      } else {
        resolve({ ok: false, error: stderr.trim() || 'ffmpeg exited with error' });
      }
    });
  });
}

export default router;




