import type { ButtonHTMLAttributes, ReactNode } from "react";

type ButtonVariant = "primary" | "secondary";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  wide?: boolean;
  children: ReactNode;
}

export function Button({
  variant = "primary",
  wide = false,
  className = "",
  children,
  ...props
}: ButtonProps) {
  const classes = [
    "button",
    `button-${variant}`,
    wide ? "button-wide" : "",
    className,
  ]
    .filter(Boolean)
    .join(" ");

  return (
    <button className={classes} {...props}>
      {children}
    </button>
  );
}
