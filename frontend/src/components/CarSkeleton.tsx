export default function CarSkeleton() {
  return (
    <article className="car-card car-card--skeleton" aria-hidden="true">
      <div className="car-card__image-wrap skeleton-block" />
      <div className="car-card__body">
        <div className="skeleton-line skeleton-line--short" />
        <div className="skeleton-line skeleton-line--long" />
        <div className="skeleton-line skeleton-line--medium" />
        <div className="car-card__footer">
          <div className="skeleton-line skeleton-line--price" />
          <div className="skeleton-btn" />
        </div>
      </div>
    </article>
  );
}