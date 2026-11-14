import { useCallback, useEffect, useRef, useState } from 'react';
import { errorMessage } from '../services/api';

export function useAsync<T>(fn: () => Promise<T>, deps: unknown[]) {
  const [data, setData] = useState<T | undefined>(undefined);
  const [error, setError] = useState<string | undefined>(undefined);
  const [loading, setLoading] = useState(true);
  const ticket = useRef(0);

  const run = useCallback(() => {
    const id = ++ticket.current;
    setLoading(true);
    setError(undefined);
    fn()
      .then((d) => { if (id === ticket.current) setData(d); })
      .catch((e) => { if (id === ticket.current) setError(errorMessage(e)); })
      .finally(() => { if (id === ticket.current) setLoading(false); });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);

  useEffect(() => {
    run();
    return () => { ticket.current++; };
  }, [run]);

  return { data, error, loading, reload: run };
}
