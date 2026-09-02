import { describe, expect, it } from 'vitest'
import { formatDocumentTitle } from './use-document-title'

describe('formatDocumentTitle', () => {
    it('uses the app title without a page title', () => {
        expect(formatDocumentTitle()).toBe('iPrompt')
    })

    it('appends a route title when present', () => {
        expect(formatDocumentTitle('Prompt Library')).toBe('iPrompt | Prompt Library')
    })

    it('ignores blank route titles', () => {
        expect(formatDocumentTitle('   ')).toBe('iPrompt')
    })
})
