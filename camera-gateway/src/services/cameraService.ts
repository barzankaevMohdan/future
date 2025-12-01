import { prisma } from '../prismaClient';
import { decrypt } from '../utils/encryption';

type CameraRecord = NonNullable<Awaited<ReturnType<typeof prisma.camera.findUnique>>>;

export async function getCameraById(cameraId: number): Promise<CameraRecord | null> {
  return prisma.camera.findUnique({
    where: { id: cameraId },
  });
}

export async function listActiveCameras(): Promise<CameraRecord[]> {
  return prisma.camera.findMany({
    where: {
      isActive: true,
    },
    orderBy: { id: 'asc' },
  });
}

export function buildRtspUrl(camera: CameraRecord): string {
  const password = decrypt(camera.passwordEnc);
  return `rtsp://${encodeURIComponent(camera.username)}:${encodeURIComponent(password)}@${camera.ip}:${camera.rtspPort}${camera.rtspPath}`;
}

export function buildSafeRtspUrl(camera: CameraRecord): string {
  return `rtsp://${encodeURIComponent(camera.username)}@${camera.ip}:${camera.rtspPort}${camera.rtspPath}`;
}

