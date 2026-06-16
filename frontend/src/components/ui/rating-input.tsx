type RatingInputProps = {
    label: string
    value: number
    onChange: (value: number) => void
    error?: string
    disabled?: boolean
}

const RATINGS = [1, 2, 3, 4, 5]

export function RatingInput({ label, value, onChange, error, disabled }: RatingInputProps) {
    return (
        <div className="field">
            <span className="label">{label}</span>
            <div className="rating-group" role="radiogroup" aria-label={label}>
                {RATINGS.map((rating) => (
                    <button
                        key={rating}
                        type="button"
                        className={`rating-button ${value === rating ? 'rating-button-active' : ''}`.trim()}
                        aria-checked={value === rating}
                        role="radio"
                        disabled={disabled}
                        onClick={() => onChange(rating)}
                    >
                        {rating}
                    </button>
                ))}
            </div>
            {error ? <p className="field-error">{error}</p> : null}
        </div>
    )
}
