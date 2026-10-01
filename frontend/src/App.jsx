import { Routes, Route, Navigate, useLocation } from 'react-router-dom'
import './LandingPage.css'
import './pages/tom-pages.css'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { AuthProvider } from './context/AuthProvider'
import Navbar from './components/Navbar'
import ChatWidget from './components/ChatWidget'
import LandingPage from './pages/LandingPage'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import ForgotPasswordPage from './pages/ForgotPasswordPage'
import ResetPasswordPage from './pages/ResetPasswordPage'
import ProfilePage from './pages/ProfilePage'
import SchedulePage from './pages/SchedulePage'
import EventDetailPage from './pages/EventDetailPage'
import LeaderboardPage from './pages/LeaderboardPage'
import AthletesPage from './pages/AthletesPage'
import AthleteProfilePage from './pages/AthleteProfilePage'
import MyTicketsPage from './pages/MyTicketsPage'
import AdminPage from './pages/AdminPage'
import VenuesPage from './pages/VenuesPage'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { refetchOnWindowFocus: false },
  },
})

function AppLayout() {
  const location = useLocation()
  const hiddenNavRoutes = ['/']
  const showNav = !hiddenNavRoutes.includes(location.pathname)

  return (
    <>
      {showNav && <Navbar />}
      <ChatWidget />
      <main>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/home" element={<Navigate to="/venues" replace />} />
          <Route path="/schedule" element={<SchedulePage />} />
          <Route path="/event/:id" element={<EventDetailPage />} />
          <Route path="/leaderboard" element={<LeaderboardPage />} />
          <Route path="/athletes" element={<AthletesPage />} />
          <Route path="/athlete/:id" element={<AthleteProfilePage />} />
          <Route path="/venues" element={<VenuesPage />} />
          <Route path="/my-tickets" element={<MyTicketsPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/forgot-password" element={<ForgotPasswordPage />} />
          <Route path="/reset-password/:uid/:token" element={<ResetPasswordPage />} />
          <Route path="/profile/:username" element={<ProfilePage />} />
          <Route path="/admin" element={<AdminPage />} />
        </Routes>
      </main>
    </>
  )
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <AppLayout />
      </AuthProvider>
    </QueryClientProvider>
  )
}

export default App
