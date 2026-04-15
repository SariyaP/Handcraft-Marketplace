"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { getStoredToken, getStoredUser, hasRequiredRole } from "../../../lib/auth";
import { createProductOrder, fetchProduct } from "../../../lib/products";
import { createProductReview } from "../../../lib/reviews";

export default function ProductDetailPage({ params }) {
  const router = useRouter();
  const [product, setProduct] = useState(null);
  const [viewer, setViewer] = useState(null);
  const [quantity, setQuantity] = useState(1);
  const [selectedChoices, setSelectedChoices] = useState({});
  const [orderMessage, setOrderMessage] = useState("");
  const [reviewValues, setReviewValues] = useState({
    rating: "5",
    comment: "",
  });
  const [reviewMessage, setReviewMessage] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const [reviewError, setReviewError] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isReviewSubmitting, setIsReviewSubmitting] = useState(false);

  useEffect(() => {
    setViewer(getStoredUser());

    async function loadProduct() {
      setIsLoading(true);
      setErrorMessage("");

      try {
        const data = await fetchProduct(params.id);
        setProduct(data);
        setSelectedChoices(
          Object.fromEntries(
            (data.customization_options || []).map((option) => [option.id, ""])
          )
        );
      } catch (error) {
        setErrorMessage(error.message || "Unable to load this product.");
      } finally {
        setIsLoading(false);
      }
    }

    loadProduct();
  }, [params.id]);

  function handleChoiceChange(optionId, choiceId) {
    setSelectedChoices((current) => ({
      ...current,
      [optionId]: choiceId,
    }));
  }

  function handleReviewChange(event) {
    const { name, value } = event.target;
    setReviewValues((current) => ({
      ...current,
      [name]: value,
    }));
  }

  async function handleOrderSubmit(event) {
    event.preventDefault();
    setErrorMessage("");
    setOrderMessage("");

    const token = getStoredToken();
    const user = getStoredUser();

    if (!token || !user || !hasRequiredRole(user, ["customer"])) {
      setErrorMessage("Sign in as a customer to order this product.");
      return;
    }

    const missingRequiredOption = product.customization_options.find(
      (option) => option.is_required && !selectedChoices[option.id]
    );
    if (missingRequiredOption) {
      setErrorMessage(`Please select ${missingRequiredOption.name}.`);
      return;
    }

    setIsSubmitting(true);
    try {
      const payload = await createProductOrder(params.id, token, {
        quantity,
        selections: Object.entries(selectedChoices)
          .filter(([, choiceId]) => Boolean(choiceId))
          .map(([optionId, choiceId]) => ({
            option_id: Number(optionId),
            choice_id: Number(choiceId),
          })),
      });
      setOrderMessage(
        `Order #${payload.id} placed successfully. You can track it in My orders.`
      );
      router.push("/products");
    } catch (error) {
      setErrorMessage(error.message || "Unable to place this order.");
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleReviewSubmit(event) {
    event.preventDefault();
    setReviewError("");
    setReviewMessage("");

    const token = getStoredToken();
    const user = getStoredUser();

    if (!token || !user || !hasRequiredRole(user, ["customer"])) {
      setReviewError("Sign in as a customer to leave a review.");
      return;
    }

    setIsReviewSubmitting(true);
    try {
      const createdReview = await createProductReview(params.id, token, {
        rating: Number(reviewValues.rating),
        comment: reviewValues.comment || null,
      });
      setProduct((current) => ({
        ...current,
        reviews: [createdReview, ...(current.reviews || [])],
      }));
      setViewer(user);
      setReviewValues({
        rating: "5",
        comment: "",
      });
      setReviewMessage("Review submitted.");
    } catch (error) {
      setReviewError(error.message || "Unable to submit your review.");
    } finally {
      setIsReviewSubmitting(false);
    }
  }

  const existingReview = product?.reviews?.find((review) => review.customer_id === viewer?.id);
  const averageRating =
    product?.reviews?.length > 0
      ? product.reviews.reduce((sum, review) => sum + review.rating, 0) / product.reviews.length
      : null;

  if (isLoading) {
    return (
      <main className="page">
        <section className="card product-detail-card">
          <p className="eyebrow">Loading</p>
          <h1>Loading product...</h1>
          <p>Fetching product details from the API.</p>
        </section>
      </main>
    );
  }

  if (!product) {
    return (
      <main className="page">
        <section className="card product-detail-card">
          <p className="eyebrow">Product Error</p>
          <h1>Unable to load product</h1>
          <p>{errorMessage || "This product could not be found."}</p>
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
      <section className="card product-detail-card">
        <div className="product-detail-layout">
          <div className="product-detail-image" aria-hidden="true">
            <span>Handcraft</span>
          </div>
          <div className="product-detail-content">
            <p className="eyebrow">Product Details</p>
            <h1>{product.name}</h1>
            <p>{product.description || "No description available yet."}</p>
            <div className="user-summary">
              <div>
                <span>Price</span>
                <strong>${Number(product.price).toFixed(2)}</strong>
              </div>
              <div>
                <span>Maker</span>
                <strong>
                  <Link href={`/maker/${product.maker_id}`}>{product.maker_name}</Link>
                </strong>
              </div>
              <div>
                <span>Stock</span>
                <strong>{product.stock_quantity}</strong>
              </div>
              <div>
                <span>Rating</span>
                <strong>
                  {averageRating ? `${averageRating.toFixed(1)} / 5` : "No reviews yet"}
                </strong>
              </div>
            </div>
            <form className="product-order-form" onSubmit={handleOrderSubmit}>
              <div className="form-field">
                <span>Quantity</span>
                <input
                  className="form-input"
                  type="number"
                  min="1"
                  max={product.stock_quantity || 50}
                  value={quantity}
                  onChange={(event) => setQuantity(Number(event.target.value))}
                  disabled={isSubmitting}
                />
              </div>
              {product.customization_options?.map((option) => (
                <label className="form-field" htmlFor={`option-${option.id}`} key={option.id}>
                  <span>{option.name}</span>
                  <select
                    id={`option-${option.id}`}
                    className="form-input"
                    value={selectedChoices[option.id] || ""}
                    onChange={(event) => handleChoiceChange(option.id, event.target.value)}
                    disabled={isSubmitting}
                    required={option.is_required}
                  >
                    <option value="">Select {option.name.toLowerCase()}</option>
                    {option.choices.map((choice) => (
                      <option key={choice.id} value={choice.id}>
                        {choice.label}
                        {Number(choice.price_delta) > 0
                          ? ` (+$${Number(choice.price_delta).toFixed(2)})`
                          : ""}
                      </option>
                    ))}
                  </select>
                </label>
              ))}
              {errorMessage ? <p className="form-message">{errorMessage}</p> : null}
              {orderMessage ? <p className="form-message form-message-success">{orderMessage}</p> : null}
              <div className="dashboard-actions">
                <button className="form-submit" type="submit" disabled={isSubmitting}>
                  {isSubmitting ? "Placing order..." : "Order with customization"}
                </button>
                <Link className="ghost-link" href="/products">
                  Back to products
                </Link>
              </div>
            </form>

            <section className="review-section">
              <div className="review-section-header">
                <div>
                  <p className="eyebrow">Product Reviews</p>
                  <h2>Customer feedback</h2>
                </div>
                <span className="rating-badge">
                  {product.reviews?.length ? `${product.reviews.length} review(s)` : "No ratings yet"}
                </span>
              </div>

              {viewer && hasRequiredRole(viewer, ["customer"]) ? (
                existingReview ? (
                  <div className="progress-item">
                    <strong>Your review</strong>
                    <p>
                      Rated {existingReview.rating}/5
                      {existingReview.comment ? `: ${existingReview.comment}` : "."}
                    </p>
                  </div>
                ) : (
                  <form className="maker-form review-form" onSubmit={handleReviewSubmit}>
                    <div className="maker-form-grid">
                      <label className="form-field" htmlFor="rating">
                        <span>Rating</span>
                        <select
                          id="rating"
                          name="rating"
                          className="form-input"
                          value={reviewValues.rating}
                          onChange={handleReviewChange}
                          disabled={isReviewSubmitting}
                        >
                          {[5, 4, 3, 2, 1].map((value) => (
                            <option key={value} value={value}>
                              {value} / 5
                            </option>
                          ))}
                        </select>
                      </label>
                      <label className="form-field" htmlFor="review-comment">
                        <span>Comment</span>
                        <textarea
                          id="review-comment"
                          name="comment"
                          className="form-input maker-textarea"
                          rows={4}
                          value={reviewValues.comment}
                          onChange={handleReviewChange}
                          disabled={isReviewSubmitting}
                          placeholder="Share what you liked about the product."
                        />
                      </label>
                    </div>
                    {reviewError ? <p className="form-message">{reviewError}</p> : null}
                    {reviewMessage ? (
                      <p className="form-message form-message-success">{reviewMessage}</p>
                    ) : null}
                    <button className="form-submit" type="submit" disabled={isReviewSubmitting}>
                      {isReviewSubmitting ? "Submitting..." : "Submit review"}
                    </button>
                  </form>
                )
              ) : (
                <div className="products-empty-state">
                  <p>Sign in as a customer to rate this product and leave feedback.</p>
                </div>
              )}

              {product.reviews?.length ? (
                <div className="review-list">
                  {product.reviews.map((review) => (
                    <article className="review-item" key={review.id}>
                      <div className="review-header">
                        <div>
                          <strong>{review.customer_name}</strong>
                          <p>{new Date(review.created_at).toLocaleDateString()}</p>
                        </div>
                        <span className="rating-badge">{review.rating} / 5</span>
                      </div>
                      <p>{review.comment || "No written comment provided."}</p>
                    </article>
                  ))}
                </div>
              ) : (
                <div className="products-empty-state">
                  <p>No reviews yet. Be the first customer to leave feedback.</p>
                </div>
              )}
            </section>
          </div>
        </div>
      </section>
    </main>
  );
}
