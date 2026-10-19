import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import BodyCareQuiz from './BodyCareQuiz.jsx'

createRoot(document.getElementById('root')).render(
    <StrictMode>
        <BodyCareQuiz />
    </StrictMode>,
)