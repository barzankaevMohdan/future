import { Router } from 'express';
import { listActiveCameras, getCameraById, buildSafeRtspUrl } from '../services/cameraService';

const router = Router();

router.get('/cameras', async (_req, res, next) => {
  try {
    const cameras = await listActiveCameras();
    res.json(
      cameras.map((camera) => ({
        id: camera.id,
        name: camera.name,
        companyId: camera.companyId,
        location: camera.location,
        ip: camera.ip,
        rtspPort: camera.rtspPort,
        rtspPath: camera.rtspPath,
        isActive: camera.isActive,
        recognitionEnabled: camera.recognitionEnabled,
        safeRtspUrl: buildSafeRtspUrl(camera),
        createdAt: camera.createdAt,
        updatedAt: camera.updatedAt,
      }))
    );
  } catch (error) {
    next(error);
  }
});

router.get('/cameras/:id', async (req, res, next) => {
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

    res.json({
      id: camera.id,
      name: camera.name,
      companyId: camera.companyId,
      location: camera.location,
      ip: camera.ip,
      rtspPort: camera.rtspPort,
      rtspPath: camera.rtspPath,
      isActive: camera.isActive,
      recognitionEnabled: camera.recognitionEnabled,
      safeRtspUrl: buildSafeRtspUrl(camera),
      createdAt: camera.createdAt,
      updatedAt: camera.updatedAt,
    });
  } catch (error) {
    next(error);
  }
});

export default router;




