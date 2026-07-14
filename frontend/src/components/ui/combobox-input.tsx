import {
    useRef,
    useState,
    type ChangeEvent,
    type KeyboardEvent,
} from 'react'
import type { SelectOption } from '../../features/options/options-types'

type ComboboxInputProps = {
    label: string
    options: SelectOption[]
    value: string
    disabled?: boolean
    error?: string
    id?: string
    placeholder?: string
    onChange: (value: string) => void
}

function optionDisplayValue(value: string, options: SelectOption[]) {
    return options.find((option) => option.value === value)?.label ?? value
}

function optionMatches(option: SelectOption, search: string) {
    const normalizedSearch = search.toLowerCase()
    return (
        option.label.toLowerCase().includes(normalizedSearch) ||
        option.value.toLowerCase().includes(normalizedSearch)
    )
}

export function ComboboxInput({
    label,
    options,
    value,
    disabled = false,
    error,
    id,
    placeholder = 'Type to search',
    onChange,
}: ComboboxInputProps) {
    const inputId = id ?? label.toLowerCase().replace(/\s+/g, '-')
    const listboxId = `${inputId}-options`
    const inputRef = useRef<HTMLInputElement>(null)
    const [isOpen, setIsOpen] = useState(false)
    const [activeIndex, setActiveIndex] = useState(0)

    const inputValue = optionDisplayValue(value, options)
    const search = inputValue.trim()
    const filteredOptions = search
        ? options.filter((option) => optionMatches(option, search))
        : options
    const selectedOption = options.find((option) => option.value === value)
    const hasUnknownValue = value.trim().length > 0 && options.length > 0 && !selectedOption
    const guidance = hasUnknownValue ? 'Select a known model from the list.' : null
    const showOptions = isOpen && !disabled && filteredOptions.length > 0
    const activeOptionIndex = Math.min(activeIndex, Math.max(filteredOptions.length - 1, 0))

    const selectOption = (option: SelectOption) => {
        onChange(option.value)
        setIsOpen(false)
        setActiveIndex(0)
        inputRef.current?.focus()
    }

    const handleInputChange = (event: ChangeEvent<HTMLInputElement>) => {
        const nextValue = event.target.value
        setActiveIndex(0)
        setIsOpen(true)
        onChange(nextValue)
    }

    const handleKeyDown = (event: KeyboardEvent<HTMLInputElement>) => {
        if (event.key === 'Escape') {
            setIsOpen(false)
            return
        }

        if (event.key === 'ArrowDown') {
            event.preventDefault()
            setIsOpen(true)
            setActiveIndex((current) => Math.min(current + 1, Math.max(filteredOptions.length - 1, 0)))
            return
        }

        if (event.key === 'ArrowUp') {
            event.preventDefault()
            setActiveIndex((current) => Math.max(current - 1, 0))
            return
        }

        if (event.key === 'Enter' && showOptions) {
            event.preventDefault()
            const option = filteredOptions[activeOptionIndex]
            if (option) {
                selectOption(option)
            }
        }
    }

    return (
        <div className="field field-combobox">
            <label htmlFor={inputId} className="label">
                {label}
            </label>
            <input
                ref={inputRef}
                id={inputId}
                className="input"
                role="combobox"
                aria-autocomplete="list"
                aria-controls={listboxId}
                aria-expanded={showOptions}
                aria-invalid={Boolean(error || guidance)}
                value={inputValue}
                disabled={disabled}
                placeholder={placeholder}
                onBlur={() => setIsOpen(false)}
                onChange={handleInputChange}
                onFocus={() => setIsOpen(true)}
                onKeyDown={handleKeyDown}
            />
            {showOptions ? (
                <div id={listboxId} className="combobox-options" role="listbox">
                    {filteredOptions.map((option, index) => (
                        <button
                            key={option.value}
                            type="button"
                            role="option"
                            aria-selected={option.value === value}
                            className={
                                index === activeOptionIndex
                                    ? 'combobox-option combobox-option-active'
                                    : 'combobox-option'
                            }
                            onMouseDown={(event) => event.preventDefault()}
                            onClick={() => selectOption(option)}
                        >
                            <span>{option.label}</span>
                            <span className="muted">{option.value}</span>
                        </button>
                    ))}
                </div>
            ) : null}
            {error ? <p className="field-error">{error}</p> : null}
            {!error && guidance ? <p className="field-error">{guidance}</p> : null}
        </div>
    )
}
