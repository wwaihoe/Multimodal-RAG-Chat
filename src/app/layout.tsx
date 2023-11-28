import type { Metadata } from 'next'
import { Roboto } from 'next/font/google'
import './globals.css'

const roboto = Roboto({ subsets: ["latin"], weight: "300" })

export const metadata: Metadata = {
  title: 'RAG Chatbot',
  description: 'Retrieval-augmented generation chatbot app',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={roboto.className}>{children}</body>
    </html>
  )
}
