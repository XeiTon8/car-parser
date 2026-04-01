function formatMileage(km: number) {
  return `${Math.round(km).toLocaleString("en-US")} km`;
}

function formatPrice(usd: number) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(usd);
}

export interface Car {
  id?: number;
  brand: string;
  model: string;
  year: number;
  mileage: number;
  price: number;
  image_url: string;
}

interface CarCardProps {
  car: Car;
}

export default function CarCard ({ car }: CarCardProps ) {
  const title = `${car.brand} ${car.model}`;

  return (
 <article className="car-card">
      <div className="car-card__image-wrap">
       
        {car.image_url ? (
          <img
            className="car-card__image"
            src={car.image_url}
            alt={title}
            loading="lazy"
          />
        ) : (
          <div className="car-card__image-fallback">No photo</div>
        )}

        <div className="car-card__year-badge">{car.year}</div>

      </div>
 
      <div className="car-card__body">
        <span className="car-card__brand">{car.brand}</span>
        <h3 className="car-card__title">{car.model}</h3>
        <span className="car-card__mileage">{formatMileage(car.mileage)}</span>
 
        <div className="car-card__footer">
          <span className="car-card__price">{formatPrice(car.price)}</span>
          <button className="car-card__btn" type="button">
            Inquire
          </button>
        </div>
      </div>
    </article>
  );
}