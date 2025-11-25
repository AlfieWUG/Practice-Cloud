/**
 * Main App component with routing.
 */
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme, CssBaseline } from '@mui/material';
import Dashboard from './pages/Dashboard';
import ProjectDetail from './pages/ProjectDetail';
import NewProject from './pages/NewProject';
import QuickAssess from './pages/QuickAssess';
import Layout from './components/Layout';
import { UserProvider } from './context/UserContext';
import QuickAssessAccessGuard from './components/quick-assess/QuickAssessAccessGuard';

// Create Material-UI theme
const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <UserProvider>
          <Layout>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/projects/new" element={<NewProject />} />
              <Route path="/projects/:projectId" element={<ProjectDetail />} />
              <Route path="/quick-assess" element={<QuickAssessAccessGuard />}>
                <Route index element={<QuickAssess />} />
              </Route>
            </Routes>
          </Layout>
        </UserProvider>
      </Router>
    </ThemeProvider>
  );
}

export default App;
