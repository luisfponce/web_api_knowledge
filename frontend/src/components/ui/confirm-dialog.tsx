import { useTranslation } from 'react-i18next'
import { Button } from './button'

type ConfirmDialogProps = {
    open: boolean
    title: string
    description: string
    confirmLabel?: string
    cancelLabel?: string
    busy?: boolean
    onConfirm: () => void
    onCancel: () => void
}

export function ConfirmDialog({
    open,
    title,
    description,
    confirmLabel = 'Confirm',
    cancelLabel = 'Cancel',
    busy = false,
    onConfirm,
    onCancel,
}: ConfirmDialogProps) {
    const { t } = useTranslation()

    if (!open) return null

    return (
        <div className="dialog-backdrop" role="presentation" onMouseDown={onCancel}>
            <div
                className="dialog-panel"
                role="dialog"
                aria-modal="true"
                aria-labelledby="confirm-dialog-title"
                onMouseDown={(event) => event.stopPropagation()}
            >
                <h2 id="confirm-dialog-title">{title}</h2>
                <p className="muted">{description}</p>
                <div className="dialog-actions">
                    <Button variant="ghost" onClick={onCancel} disabled={busy}>
                        {cancelLabel}
                    </Button>
                    <Button variant="danger" onClick={onConfirm} disabled={busy}>
                        {busy ? t('common.working') : confirmLabel}
                    </Button>
                </div>
            </div>
        </div>
    )
}
