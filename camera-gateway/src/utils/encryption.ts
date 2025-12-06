import crypto from 'crypto';
import { config } from '../config';

const ALGORITHM = 'aes-256-cbc';
const KEY = Buffer.from(config.encryptionKey.padEnd(32, '0').slice(0, 32));

export function decrypt(text: string): string {
  const [ivHex, encryptedText] = text.split(':');
  if (!ivHex || !encryptedText) {
    throw new Error('Invalid encrypted payload');
  }
  const iv = Buffer.from(ivHex, 'hex');
  const decipher = crypto.createDecipheriv(ALGORITHM, KEY, iv);
  let decrypted = decipher.update(encryptedText, 'hex', 'utf8');
  decrypted += decipher.final('utf8');
  return decrypted;
}

