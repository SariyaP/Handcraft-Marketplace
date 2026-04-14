"use client";

export default function FormMessage({ type = "error", message }) {
  if (!message) {
    return null;
  }

  return (
    <p className={type === "success" ? "form-message form-message-success" : "form-message"}>
      {message}
    </p>
  );
}
