"use client";

import { useEffect, useState } from "react";

import Link from "next/link";

import AppShell from "../../../components/ui/AppShell";
import { LoadingState } from "../../../components/ui/StateCard";
import { getLogoutAction, getMakerNav } from "../../../lib/navigation";
import { useRequireRole } from "../../../lib/useRequireRole";
import { fetchOwnMakerProfile, updateOwnMakerProfile } from "../../../lib/makers";

const initialValues = {
  shop_name: "",
  bio: "",
  specialization: "",
  profile_image_url: "",
};

export default function MakerProfilePage() {
  const { user, token, isCheckingAuth } = useRequireRole("maker");
  const [values, setValues] = useState(initialValues);
  const [profile, setProfile] = useState(null);
  const [message, setMessage] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (isCheckingAuth || !token) {
      return;
    }

    async function loadPage() {
      setIsLoading(true);
      try {
        const makerProfile = await fetchOwnMakerProfile(token);
        setProfile(makerProfile);
        setValues({
          shop_name: makerProfile.shop_name || "",
          bio: makerProfile.bio || "",
          specialization: makerProfile.specialization || "",
          profile_image_url: makerProfile.profile_image_url || "",
        });
      } catch (error) {
        setErrorMessage(error.message || "Unable to load maker profile.");
      } finally {
        setIsLoading(false);
      }
    }

    loadPage();
  }, [isCheckingAuth, token]);

  function handleChange(event) {
    const { name, value } = event.target;
    setValues((current) => ({
      ...current,
      [name]: value,
    }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    if (!token) {
      return;
    }

    setIsSubmitting(true);
    setMessage("");
    setErrorMessage("");

    try {
      const updatedProfile = await updateOwnMakerProfile(token, values);
      setProfile(updatedProfile);
      setMessage("Maker profile updated.");
    } catch (error) {
      setErrorMessage(error.message || "Unable to update maker profile.");
    } finally {
      setIsSubmitting(false);
    }
  }

  if (isCheckingAuth || isLoading) {
    return (
      <AppShell
        eyebrow="Maker Profile"
        title="Shop profile"
        description="Edit the public maker details customers see."
        navItems={getMakerNav("profile")}
        actions={getLogoutAction()}
      >
        <section className="card content-card">
          <LoadingState title="Loading maker profile..." description="Fetching your public maker details." />
        </section>
      </AppShell>
    );
  }

  return (
    <AppShell
      eyebrow="Maker Profile"
      title={user ? `${user.full_name}'s shop profile` : "Edit maker profile"}
      description="Update the public details customers see on your maker page."
      navItems={getMakerNav("profile")}
      actions={getLogoutAction()}
    >
      <section className="card content-card maker-profile-card">
        <div className="section-header">
          <div>
            <p className="eyebrow">Public Profile</p>
            <h2>{user ? `${user.full_name}'s public profile` : "Edit maker profile"}</h2>
            <p>Update the public details customers see on your maker page.</p>
          </div>
        </div>

        {message ? <p className="form-message form-message-success">{message}</p> : null}
        {errorMessage ? <p className="form-message">{errorMessage}</p> : null}

        <div className="maker-profile-layout">
          <form className="maker-panel maker-form" onSubmit={handleSubmit}>
            <label className="form-field" htmlFor="shop_name">
              <span>Shop name</span>
              <input
                id="shop_name"
                name="shop_name"
                className="form-input"
                value={values.shop_name}
                onChange={handleChange}
                required
                disabled={isSubmitting}
              />
            </label>
            <label className="form-field" htmlFor="bio">
              <span>Bio</span>
              <textarea
                id="bio"
                name="bio"
                className="form-input maker-textarea"
                rows={5}
                value={values.bio}
                onChange={handleChange}
                disabled={isSubmitting}
              />
            </label>
            <label className="form-field" htmlFor="specialization">
              <span>Specialization</span>
              <input
                id="specialization"
                name="specialization"
                className="form-input"
                value={values.specialization}
                onChange={handleChange}
                disabled={isSubmitting}
              />
            </label>
            <label className="form-field" htmlFor="profile_image_url">
              <span>Profile image URL</span>
              <input
                id="profile_image_url"
                name="profile_image_url"
                type="url"
                className="form-input"
                value={values.profile_image_url}
                onChange={handleChange}
                disabled={isSubmitting}
              />
            </label>
            <button className="form-submit" type="submit" disabled={isSubmitting}>
              {isSubmitting ? "Saving..." : "Save profile"}
            </button>
          </form>

          <section className="maker-panel maker-profile-preview">
            <p className="eyebrow">Preview</p>
            <div className="maker-public-hero">
              <div className="maker-avatar-frame">
                {profile?.profile_image_url || values.profile_image_url ? (
                  // eslint-disable-next-line @next/next/no-img-element
                  <img
                    className="maker-avatar-image"
                    src={profile?.profile_image_url || values.profile_image_url}
                    alt={values.shop_name || "Maker profile"}
                  />
                ) : (
                  <div className="maker-avatar-fallback">Maker</div>
                )}
              </div>
              <div className="maker-public-copy">
                <h2>{values.shop_name || "Your shop name"}</h2>
                <p>{values.bio || "Your bio will appear here."}</p>
                <div className="maker-public-tags">
                  <span>{values.specialization || "Specialization"}</span>
                  <span>{profile?.verification_status || "unverified"}</span>
                </div>
                <div className="dashboard-actions">
                  <Link className="ghost-link" href={`/maker/${profile?.user_id || user?.id}`}>
                    View public page
                  </Link>
                </div>
              </div>
            </div>
          </section>
        </div>
      </section>
    </AppShell>
  );
}
