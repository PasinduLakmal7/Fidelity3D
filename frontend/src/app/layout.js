import './globals.css'

export const metadata = {
  title: 'Fidelity3D - AI 3D Generation',
  description: 'Transform 2D images into animated 3D models in seconds.',
}

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
