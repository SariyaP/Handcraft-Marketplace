"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { fetchPublicMakerProfile } from "../../../lib/makers";

export default function PublicMakerProfilePage({ params }) {
  const [profile, setProfile] = useState(null);
  const [errorMessage, setErrorMessage] = useState("");
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function loadProfile() {
      setIsLoading(true);
      setErrorMessage("");

      try {
        const makerProfile = await fetchPublicMakerProfile(params.id);
        setProfile(makerProfile);
      } catch (error) {
        setErrorMessage(error.message || "Unable to load maker profile.");
      } finally {
        setIsLoading(false);
      }
    }

    loadProfile();
  }, [params.id]);

  if (isLoading) {
    return (
      <main className="page">
        <section className="card maker-profile-card">
          <p className="eyebrow">Loading</p>
          <h1>Loading maker profile...</h1>
          <p>Fetching public maker details.</p>
        </section>
      </main>
    );
  }

  if (!profile) {
    return (
      <main className="page">
        <section className="card maker-profile-card">
          <p className="eyebrow">Profile Error</p>
          <h1>Maker profile not found</h1>
          <p>{errorMessage || "This maker profile could not be found."}</p>
          <div className="dashboard-actions">
            <Link className="ghost-link" href="/products">
              Back to products
            </Link>
          </div>
        </section>
      </main>
    );
  }

  return (
    <main className="page">
      <section className="card maker-profile-card">
        <div className="products-header">
          <div>
            <p className="eyebrow">Maker Profile</p>
            <h1>{profile.shop_name}</h1>
            <p>Public maker storefront information.</p>
          </div>
          <div className="dashboard-actions">
            <Link className="ghost-link" href="/products">
              Back to products
            </Link>
          </div>
        </div>

        <div className="maker-public-hero maker-public-hero-wide">
          <div className="maker-avatar-frame">
            {profile.profile_image_url ? (
              // eslint-disable-next-line @next/next/no-img-element
              <img
                className="maker-avatar-image"
                src={profile.profile_image_url}
                alt={profile.shop_name}
              />
            ) : (
              <div className="maker-avatar-fallback">Maker</div>
            )}
          </div>
          <div className="maker-public-copy">
            <h2>{profile.full_name}</h2>
            <p>{profile.bio || "This maker has not added a bio yet."}</p>
            <div className="maker-public-tags">
              <span>{profile.specialization || "General handmade goods"}</span>
              <span>{profile.verification_status}</span>
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}
