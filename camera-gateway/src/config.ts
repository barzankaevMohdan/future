import dotenv from 'dotenv';

dotenv.config();

function requireEnv(name: string, fallback?: string): string {
  const value = process.env[name] ?? fallback;
  if (!value) {
    throw new Error(`Missing required environment variable ${name}`);
  }
  return value;
}

export const config = {
  port: parseInt(process.env.PORT || '4000', 10),
  nodeEnv: process.env.NODE_ENV || 'development',
  databaseUrl: requireEnv('DATABASE_URL'),
  encryptionKey: requireEnv('ENCRYPTION_KEY'),
  ffmpegPath: process.env.FFMPEG_PATH || 'ffmpeg',
  streamIdleTimeoutMs: parseInt(process.env.STREAM_IDLE_TIMEOUT_MS || '15000', 10),
  maxRestartsPerWindow: parseInt(process.env.MAX_RESTARTS_PER_WINDOW || '5', 10),
  restartWindowMs: parseInt(process.env.RESTART_WINDOW_MS || '300000', 10),
} as const;

