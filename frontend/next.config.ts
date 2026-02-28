import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  webpack: (config, { nextRuntime, webpack }) => {
    if (nextRuntime === 'edge') {
      // The @next/env ncc bundle uses `__dirname` for base-path resolution.
      // Edge Runtime doesn't provide __dirname, causing a ReferenceError crash.
      // BannerPlugin injects this polyfill as raw JS at the TOP of the compiled
      // chunk — before any module code runs — guaranteeing __dirname exists.
      config.plugins.push(
        new webpack.BannerPlugin({
          banner: 'if(typeof __dirname==="undefined"){globalThis.__dirname="/"}if(typeof __filename==="undefined"){globalThis.__filename="/index.js"}',
          raw: true,
          entryOnly: false,
        })
      );

      // Stub out Node.js built-ins that don't exist in Edge Runtime
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
