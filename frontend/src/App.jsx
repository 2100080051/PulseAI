import { Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import Footer from './components/Footer'
import HomePage from './pages/HomePage'
import CategoryPage from './pages/CategoryPage'
import SearchPage from './pages/SearchPage'

export default function App() {
  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Navbar />
      <main style={{ flex: 1, paddingTop: 0 }}>
        <Routes>
          <Route path="/"                element={<HomePage />} />
          <Route path="/category/:slug"  element={<CategoryPage />} />
          <Route path="/search"          element={<SearchPage />} />
          <Route path="*"                element={
            <div style={{ textAlign: 'center', paddingTop: 160, paddingBottom: 80 }}>
              <p style={{ fontSize: 72, marginBottom: 16 }}>🤖</p>
              <h1 style={{ fontSize: 36, marginBottom: 12 }}>404 — Page Not Found</h1>
              <p style={{ color: 'var(--text-muted)', marginBottom: 32 }}>This page doesn't exist yet.</p>
              <a href="/" className="btn-primary">Back to PulseAI</a>
            </div>
          } />
        </Routes>
      </main>
      <Footer />
    </div>
  )
}
