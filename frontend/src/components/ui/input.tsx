import type { InputHTMLAttributes } from 'react'

type InputProps = InputHTMLAttributes<HTMLInputElement> & {
    label: string
    error?: string
}

export function Input({ label, id, error, className = '', ...props }: InputProps) {
    const inputId = id ?? label.toLowerCase().replace(/\s+/g, '-')

    return (
        <div className="field">
            <label htmlFor={inputId} className="label">
                {label}
            </label>
            <input id={inputId} className={`input ${className}`.trim()} {...props} />
            {error ? <p className="field-error">{error}</p> : null}
        </div>
    )
}

