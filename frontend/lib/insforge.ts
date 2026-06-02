import { createClient } from "@insforge/sdk";

const baseUrl =
  process.env.NEXT_PUBLIC_INSFORGE_URL ?? "https://p43i5mjd.us-east.insforge.app";
const anonKey = process.env.NEXT_PUBLIC_INSFORGE_ANON_KEY ?? "";

export const insforge = createClient({
  baseUrl,
  anonKey,
});

export const authEnabled =
  process.env.NEXT_PUBLIC_AUTH_ENABLED === "true" && Boolean(anonKey);
