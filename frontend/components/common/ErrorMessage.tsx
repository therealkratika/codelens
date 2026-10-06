interface ErrorMessageProps {
  message: string;
  onDismiss?: () => void;
}

export function ErrorMessage({ message, onDismiss }: ErrorMessageProps) {
  return (
    <div className="error-message" role="alert">
      <p>{message}</p>
      {onDismiss ? (
        <button
          className="error-dismiss"
          type="button"
          aria-label="Dismiss error"
          onClick={onDismiss}
        >
          ×
        </button>
      ) : null}
    </div>
  );
}
