import { Router, Request, Response, NextFunction } from 'express';
import { streamManager } from '../services/streamManager';

const router = Router();

router.get('/streams/:cameraId.mjpg', async (req: Request, res: Response, next: NextFunction) => {
  try {
    const cameraId = Number(req.params.cameraId);
    if (!Number.isInteger(cameraId)) {
      res.status(400).json({ error: 'Invalid camera id' });
      return;
    }

    res.writeHead(200, {
      'Cache-Control': 'no-cache',
      'Connection': 'close',
      'Content-Type': 'multipart/x-mixed-replace; boundary=frame',
      Pragma: 'no-cache',
      'Access-Control-Allow-Origin': '*',
      'Cross-Origin-Resource-Policy': 'cross-origin',
    });

    await streamManager.attachClient(cameraId, res);
  } catch (error) {
    next(error);
  }
});

export default router;




