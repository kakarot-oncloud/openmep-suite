import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    environment: "node",
    // Allow both .js-extension imports and bare imports in TypeScript files
    alias: {},
  },
});
