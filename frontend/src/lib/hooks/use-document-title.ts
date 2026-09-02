import { useEffect } from 'react'

const APP_TITLE = 'iPrompt'

export function formatDocumentTitle(pageTitle?: string | null) {
    const trimmedTitle = pageTitle?.trim()
    return trimmedTitle ? `${APP_TITLE} | ${trimmedTitle}` : APP_TITLE
}

export function useDocumentTitle(pageTitle?: string | null) {
    useEffect(() => {
        document.title = formatDocumentTitle(pageTitle)
    }, [pageTitle])
}
