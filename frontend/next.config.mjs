import path from "node:path";

const nextConfig = {
  allowedDevOrigins: ["192.168.0.247"],
  outputFileTracingRoot: path.join(process.cwd(), ".."),
};

export default nextConfig;
