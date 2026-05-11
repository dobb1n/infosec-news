import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
  serverExternalPackages: ["@google-cloud/storage", "@google-cloud/vertexai"],
};

export default nextConfig;
