import type { SelectHTMLAttributes } from 'react'
import type { SelectOption } from '../../features/options/options-types'

type SelectProps = SelectHTMLAttributes<HTMLSelectElement> & {
    label: string
    options: SelectOption[]
    error?: string
    placeholder?: string
}

export function Select({
    label,
    id,
    options,
    error,
    placeholder = 'Select an option',
    className = '',
    ...props
}: SelectProps) {
    const inputId = id ?? label.toLowerCase().replace(/\s+/g, '-')

    return (
        <div className="field">
            <label htmlFor={inputId} className="label">
                {label}
            </label>
            <select id={inputId} className={`input ${className}`.trim()} {...props}>
                <option value="">{placeholder}</option>
                {options.map((option) => (
                    <option key={option.value} value={option.value}>
                        {option.label}
                    </option>
                ))}
            </select>
            {error ? <p className="field-error">{error}</p> : null}
        </div>
    )
}
