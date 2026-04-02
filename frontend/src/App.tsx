import { useState, useEffect } from "react";

import type { Car } from "./components/CarCard";
import { data } from "./data";

import Header from "./components/Header"
import CarGrid from "./components/CarGrid";

import "./index.css";
import Hero from "./components/Hero";

const URL = import.meta.env.VITE_API_URL;
const CARS_LIMIT = 20;

const parsedCars: Car[] = data.map((car) => ({
  id: Number(car.id),
  brand: car.brand,
  model: car.model,
  year: Number(car.year),
  mileage: Number(car.mileage),
  price: Number(car.price),
  image_url: car.image_url,
}));

export default function App() {

  const [cars, setCars] = useState<Car[]>(parsedCars);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [page, setPage] = useState(0);
  const [hasMore, setHasMore] = useState(true);

  const fakeFetchCars = (skip = 0, limit = CARS_LIMIT): Promise<Car[]> => {
  return new Promise((resolve) => {
    setTimeout(() => {
      const slice = parsedCars.slice(skip, skip + limit);
      resolve(slice);
    }, 1500);
  });
};

const fetchCars = async (skip = 0, replace = false) => {
  try {
    setLoading(true);
    setError(null);

    const data = await fakeFetchCars(skip, CARS_LIMIT);

    if (data.length < CARS_LIMIT) setHasMore(false);

    setCars((prev) => (replace ? data : [...prev, ...data]));
  } catch (err: any) {
    setError(err.message);
  } finally {
    setLoading(false);
  }
};

  useEffect(() => {
   fetchCars(0, true);
  }, []);

  const loadMore = () => {
    const nextPage = page + 1;
    setPage(nextPage);
    fetchCars(nextPage * CARS_LIMIT);
  };

  return (
    <div className="app">
      <Header />
      <Hero />
      <main className="main-content">
        <div className="section-header">
          <h2 className="section-title">Available Cars</h2>
        </div>
        <CarGrid cars={cars} loading={loading} error={error!} />
        {!loading && hasMore && cars.length > 0 && (
          <div className="load-more-wrapper">
            <button className="load-more-btn" onClick={loadMore}>
              Load More
            </button>
          </div>
        )}
      </main>
      <footer className="footer">
        <span>Some text</span>
      </footer>
    </div>
  );
}