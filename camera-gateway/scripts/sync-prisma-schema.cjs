const fs = require('fs');
const path = require('path');

const possibleSources = [
  path.resolve(__dirname, '..', '..', 'backend', 'prisma', 'schema.prisma'),
  path.resolve(__dirname, '..', 'backend-prisma', 'schema.prisma'),
];

const targetDir = path.resolve(__dirname, '..', 'prisma');
const target = path.join(targetDir, 'schema.prisma');

const source = possibleSources.find((candidate) => fs.existsSync(candidate));

if (!source) {
  console.error('Cannot find backend schema. Checked:', possibleSources);
  process.exit(1);
}

fs.mkdirSync(targetDir, { recursive: true });
fs.copyFileSync(source, target);
console.log(`Prisma schema synced to ${target}`);

