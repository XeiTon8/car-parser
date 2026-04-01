import { useState, useEffect } from "react";

import type { Car } from "./components/CarCard";

import Header from "./components/Header"
import CarGrid from "./components/CarGrid";

import "./index.css";

const URL = import.meta.env.VITE_API_URL;
const CARS_LIMIT = 20;

export default function App() {

  const [cars, setCars] = useState<Car[]>([]);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [page, setPage] = useState(0);
  const [hasMore, setHasMore] = useState(true);

  const fetchCars = async (skip = 0, replace = false) => {
    try {
      setLoading(true);

      const res = await fetch(`${URL}/cars?skip=${skip}&limit=${CARS_LIMIT}`);
      if (!res.ok) throw new Error("Failed to fetch cars");

      const data = await res.json();

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