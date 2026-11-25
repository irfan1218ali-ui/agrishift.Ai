import type { Metadata, Viewport } from "next";
import "maplibre-gl/dist/maplibre-gl.css";
import "./globals.css";

export const metadata: Metadata = {
  title: "AgriShift AI — Field-based crop rotation guidance",
  description: "Compare crop rotation strategies with satellite observations, climate history, and local agronomic review.",
  applicationName: "AgriShift AI",
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  themeColor: "#f8fafc",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en" dir="ltr" data-scroll-behavior="smooth"><body>{children}</body></html>;
}
