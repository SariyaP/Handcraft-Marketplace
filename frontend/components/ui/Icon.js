"use client";

const paths = {
  products: "M4 7.5h16M6.5 4h11a1.5 1.5 0 0 1 1.5 1.5v13A1.5 1.5 0 0 1 17.5 20h-11A1.5 1.5 0 0 1 5 18.5v-13A1.5 1.5 0 0 1 6.5 4Z",
  profile: "M12 12a3.25 3.25 0 1 0 0-6.5A3.25 3.25 0 0 0 12 12Zm0 2.5c-3.6 0-6.5 1.9-6.5 4.25V20h13v-1.25c0-2.35-2.9-4.25-6.5-4.25Z",
  commissions: "M7 5.5h10M7 10h10M7 14.5h6M6.5 4h11A1.5 1.5 0 0 1 19 5.5v13a1.5 1.5 0 0 1-1.5 1.5h-11A1.5 1.5 0 0 1 5 18.5v-13A1.5 1.5 0 0 1 6.5 4Z",
  reviews: "m8.4 14.6 3.6-2.2 3.6 2.2-.95-4.12 3.15-2.73-4.16-.36L12 3.5l-1.64 3.89-4.16.36 3.15 2.73-.95 4.12Z",
  wishlist: "M12 20s-6.5-4.35-8.6-7.76C1.4 9.02 3.35 5.5 7.02 5.5c1.97 0 3.17 1.01 4 2.15.83-1.14 2.03-2.15 4-2.15 3.67 0 5.62 3.52 3.62 6.74C18.5 15.65 12 20 12 20Z",
  admin: "M12 3.75 18.5 6v6c0 4.06-2.57 6.77-6.5 8.25C8.07 18.77 5.5 16.06 5.5 12V6L12 3.75Zm0 4.25a2.25 2.25 0 1 0 0 4.5A2.25 2.25 0 0 0 12 8Zm0 5.75c-1.85 0-3.42.92-4 2.25h8c-.58-1.33-2.15-2.25-4-2.25Z",
  login: "M14 4.5h2.5A1.5 1.5 0 0 1 18 6v12a1.5 1.5 0 0 1-1.5 1.5H14M10 16.5 13.5 12 10 7.5M13 12H5.5",
};

export default function Icon({ name, className = "ui-icon" }) {
  const path = paths[name];
  if (!path) {
    return null;
  }

  return (
    <svg
      className={className}
      viewBox="0 0 24 24"
      aria-hidden="true"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.75"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d={path} />
    </svg>
  );
}
