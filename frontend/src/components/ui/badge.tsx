import type { HTMLAttributes } from 'react'

type BadgeProps = HTMLAttributes<HTMLSpanElement> & {
    tone?: 'default' | 'accent' | 'danger'
}

export function Badge({ tone = 'default', className = '', ...props }: BadgeProps) {
    return <span className={`badge badge-${tone} ${className}`.trim()} {...props} />
}
