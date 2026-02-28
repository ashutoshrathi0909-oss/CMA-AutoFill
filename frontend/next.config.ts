import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  webpack: (config, { nextRuntime, webpack }) => {
    if (nextRuntime === 'edge') {
      // Inject __dirname/__filename polyfill at the top of EVERY chunk.
      // This ensures it runs before @next/env's ncc bundle which uses
      // __dirname for base-path resolution in Edge Runtime.
      config.plugins.push(
        new webpack.BannerPlugin({
          banner: 'if(typeof __dirname==="undefined"){globalThis.__dirname="/"}if(typeof __filename==="undefined"){globalThis.__filename="/index.js"}',
          raw: true,
          entryOnly: false,
        })
      );

      // Also replace __dirname tokens at compile time as a backup
      config.plugins.push(
        new webpack.DefinePlugin({
          __dirname: JSON.stringify('/'),
          __filename: JSON.stringify('/index.js'),
        })
      );

      // Stub Node.js built-ins that don't exist in Edge
      config.resolve.fallback = {
        ...config.resolve.fallback,
        fs: false,
        net: false,
        tls: false,
        crypto: false,
        path: false,
        os: false,
        stream: false,
        http: false,
        https: false,
        zlib: false,
      };
    }
    return config;
  },
};

export default nextConfig;
