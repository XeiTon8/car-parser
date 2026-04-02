import CarCard from "./CarCard"
import CarSkeleton from "./CarSkeleton"
import type { Car } from "./CarCard";

interface CarGridProps {
  cars: Car[];
  loading: boolean;
  error?: string;
}

export default function CarGrid({ cars, loading, error }: CarGridProps) {

  if (error) {
    return (
      <div className="error-state">
        <span className="error-icon">⚠</span>
        <span className="error-msg">Could not load listings: {error}</span>
      </div>
    );
  }

  if (loading && cars.length === 0) {
    return (
      <section className="car-grid" id="cars">
        {Array.from({ length: 8 }).map((_, i) => (
          <CarSkeleton key={i} />
        ))}
      </section>
    );
  }

  if (!loading && cars.length === 0) {
    return (
      <div className="empty-state">
        <span className="empty-msg">No listings yet.</span>
      </div>
    );
  }

  return (
    <section className="car-grid" id="cars">
      {cars.map((car) => (
        <CarCard key={car.id} car={car} />
      ))}
      {loading && cars.length > 0 &&
        Array.from({ length: 4 }).map((_, i) => (
          <CarSkeleton key={`loading-${i}`} />
        ))}
    </section>
  );
}