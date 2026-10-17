import { Navigate, Route, Routes } from 'react-router-dom'
import Layout from './components/Layout.jsx'
import ProjectsPage from './pages/ProjectsPage.jsx'
import SearchPage from './pages/SearchPage.jsx'
import StatisticsPage from './pages/StatisticsPage.jsx'
import UploadPage from './pages/UploadPage.jsx'

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<ProjectsPage />} />
        <Route path="search" element={<SearchPage />} />
        <Route path="statistics" element={<StatisticsPage />} />
        <Route path="upload" element={<UploadPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  )
}
