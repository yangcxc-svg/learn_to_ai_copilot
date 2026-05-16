import "./globals.css";

export const metadata = {
  title: "AI Customer Service Copilot",
  description: "AI 客诉辅助 Copilot MVP"
};

export default function RootLayout({
  children
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="zh-CN">
      <body>{children}</body>
    </html>
  );
}

