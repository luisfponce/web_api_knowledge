import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { RouterProvider } from 'react-router-dom'
import { AppProviders } from './app/providers'
import { router } from './app/router'
import './i18n'
import { applyTheme, getInitialTheme } from './lib/utils/theme'
import './styles/tokens.css'
import './styles/themes.css'
import './styles/base.css'

applyTheme(getInitialTheme())

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <AppProviders>
      <RouterProvider router={router} />
    </AppProviders>
  </StrictMode>,
)
