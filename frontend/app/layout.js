import "./globals.css";

const appName =
  process.env.NEXT_PUBLIC_APP_NAME ?? "Handcraft Marketplace";

export const metadata = {
  title: appName,
  description: "Starter frontend for the Handcraft Marketplace project.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
