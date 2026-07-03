import { Star, StarHalf } from 'lucide-react';

export default function Stars({ rating, size = 14 }: { rating: number; size?: number }) {
  const full = Math.floor(rating);
  const half = rating - full >= 0.4;
  return (
    <span className="inline-flex items-center">
      {[0, 1, 2, 3, 4].map((i) => {
        if (i < full) {
          return <Star key={i} style={{ width: size, height: size }} className="fill-accent-400 text-accent-400" />;
        }
        if (i === full && half) {
          return (
            <span key={i} className="relative inline-flex" style={{ width: size, height: size }}>
              <Star style={{ width: size, height: size }} className="absolute text-slate-300" />
              <StarHalf style={{ width: size, height: size }} className="absolute fill-accent-400 text-accent-400" />
            </span>
          );
        }
        return <Star key={i} style={{ width: size, height: size }} className="text-slate-300" />;
      })}
    </span>
  );
}
