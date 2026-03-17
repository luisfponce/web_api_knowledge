type InlineErrorProps = {
    message: string
}

export function InlineError({ message }: InlineErrorProps) {
    return <p className="inline-error">{message}</p>
}

