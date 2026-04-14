"use client";

export default function SubmitButton({ isLoading, children, loadingLabel }) {
  return (
    <button className="form-submit" type="submit" disabled={isLoading}>
      {isLoading ? loadingLabel : children}
    </button>
  );
}
