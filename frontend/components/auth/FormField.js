"use client";

export default function FormField({
  label,
  name,
  type = "text",
  value,
  onChange,
  placeholder,
  autoComplete,
  disabled = false,
  required = false,
  minLength,
  maxLength,
  children,
}) {
  return (
    <label className="form-field" htmlFor={name}>
      <span>{label}</span>
      {children ? (
        children
      ) : (
        <input
          id={name}
          name={name}
          type={type}
          value={value}
          onChange={onChange}
          placeholder={placeholder}
          autoComplete={autoComplete}
          disabled={disabled}
          required={required}
          minLength={minLength}
          maxLength={maxLength}
          className="form-input"
        />
      )}
    </label>
  );
}
