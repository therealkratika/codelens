export default function ErrorMessage({ message, onDismiss }) {
  if (!message) return null;
  return <div className="alert alert-error" role="alert"><span>!</span><div>{message}</div>{onDismiss && <button onClick={onDismiss} aria-label="Dismiss error">×</button>}</div>;
}
