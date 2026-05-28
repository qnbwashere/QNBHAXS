/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    remotePatterns: [
      { protocol: 'https', hostname: 'www.futbin.com' },
      { protocol: 'https', hostname: 'cdn.futbin.com' },
      { protocol: 'https', hostname: 'fut.gg' },
    ],
  },
};

module.exports = nextConfig;
