export function getCustomerNav(activeKey) {
  return [
    {
      key: "marketplace",
      href: "/products",
      label: "Marketplace",
      caption: "Browse and order",
      icon: "products",
      active: activeKey === "marketplace",
    },
    {
      key: "wishlist",
      href: "/wishlist",
      label: "Wishlist",
      caption: "Saved items",
      icon: "wishlist",
      active: activeKey === "wishlist",
    },
    {
      key: "commissions",
      href: "/commissions",
      label: "Commissions",
      caption: "Custom requests",
      icon: "commissions",
      active: activeKey === "commissions",
    },
  ];
}

export function getGuestMarketplaceNav(activeKey) {
  return [
    {
      key: "marketplace",
      href: "/products",
      label: "Marketplace",
      caption: "Public catalog",
      icon: "products",
      active: activeKey === "marketplace",
    },
    {
      key: "login",
      href: "/login",
      label: "Login",
      caption: "Customer or maker access",
      icon: "login",
      active: activeKey === "login",
    },
    {
      key: "register",
      href: "/register",
      label: "Register",
      caption: "Create an account",
      icon: "profile",
      active: activeKey === "register",
    },
  ];
}

export function getMakerNav(activeKey) {
  return [
    {
      key: "products",
      href: "/maker",
      label: "Products",
      caption: "Catalog management",
      icon: "products",
      active: activeKey === "products",
    },
    {
      key: "profile",
      href: "/maker/profile",
      label: "Profile",
      caption: "Shop details",
      icon: "profile",
      active: activeKey === "profile",
    },
    {
      key: "commissions",
      href: "/maker/commissions",
      label: "Commissions",
      caption: "Requests and WIP",
      icon: "commissions",
      active: activeKey === "commissions",
    },
    {
      key: "reviews",
      href: "/maker/reviews",
      label: "Reviews",
      caption: "Customer feedback",
      icon: "reviews",
      active: activeKey === "reviews",
    },
  ];
}

export function getAdminNav(activeKey) {
  return [
    {
      key: "moderation",
      href: "/admin",
      label: "Moderation",
      caption: "Users and content",
      icon: "admin",
      active: activeKey === "moderation",
    },
    {
      key: "marketplace",
      href: "/products",
      label: "Marketplace",
      caption: "Public view",
      icon: "products",
      active: activeKey === "marketplace",
    },
  ];
}

export function getLogoutAction() {
  return [{ type: "logout", redirectTo: "/login" }];
}
