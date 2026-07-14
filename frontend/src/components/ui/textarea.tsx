import type { TextareaHTMLAttributes } from 'react'

type TextareaProps = TextareaHTMLAttributes<HTMLTextAreaElement> & {
    label: string
    error?: string
}

export function Textarea({ label, id, error, className = '', ...props }: TextareaProps) {
    const inputId = id ?? label.toLowerCase().replace(/\s+/g, '-')

    return (
        <div className="field">
            <label htmlFor={inputId} className="label">
                {label}
            </label>
            <textarea id={inputId} className={`input textarea ${className}`.trim()} {...props} />
            {error ? <p className="field-error">{error}</p> : null}
        </div>
    )
}
