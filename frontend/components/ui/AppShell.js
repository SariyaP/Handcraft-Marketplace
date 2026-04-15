"use client";

import Link from "next/link";

import LogoutButton from "../auth/LogoutButton";

export default function AppShell({
  eyebrow,
  title,
  description,
  navItems = [],
  actions = [],
  children,
}) {
  return (
    <main className="app-shell">
      <aside className="app-sidebar">
        <div className="app-sidebar-brand">
          <p className="eyebrow">{eyebrow}</p>
          <h1>{title}</h1>
          <p>{description}</p>
        </div>

        <nav className="app-sidebar-nav" aria-label="Dashboard navigation">
          {navItems.map((item) =>
            item.href ? (
              <Link
                key={item.href}
                className={item.active ? "sidebar-link sidebar-link-active" : "sidebar-link"}
                href={item.href}
              >
                <span className="sidebar-link-label">{item.label}</span>
                {item.caption ? <small>{item.caption}</small> : null}
              </Link>
            ) : (
              <div key={item.label} className="sidebar-link sidebar-link-static">
                <span className="sidebar-link-label">{item.label}</span>
                {item.caption ? <small>{item.caption}</small> : null}
              </div>
            )
          )}
        </nav>

        <div className="app-sidebar-actions">
          {actions.map((action, index) =>
            action.type === "logout" ? (
              <LogoutButton
                key={`logout-${index}`}
                className={action.className || "ghost-button sidebar-action-button"}
                redirectTo={action.redirectTo}
              />
            ) : (
              <Link
                key={action.href || `${action.label}-${index}`}
                className={action.className || "ghost-link sidebar-action-button"}
                href={action.href}
              >
                {action.label}
              </Link>
            )
          )}
        </div>
      </aside>

      <section className="app-content">{children}</section>
    </main>
  );
}
