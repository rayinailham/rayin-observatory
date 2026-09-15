import type { NextConfig } from 'next';
const config: NextConfig = {
  reactStrictMode: true,
  transpilePackages: ['three'],
  poweredByHeader: false,
  devIndicators: false,
};
export default config;
