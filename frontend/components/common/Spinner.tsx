interface SpinnerProps {
  label?: string;
}

export function Spinner({ label }: SpinnerProps) {
  return (
    <>
      <span className="spinner" aria-hidden="true" />
      {label ? <span className="sr-only">{label}</span> : null}
    </>
  );
}
