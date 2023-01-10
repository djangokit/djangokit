import { useEffect, useRef } from "react";

export function useInterval(callback, condition, delay) {
  const callbackRef = useRef<() => void>();

  useEffect(() => {
    callbackRef.current = callback;
  }, [callback]);

  // Run callback right away to avoid delayed start.
  useEffect(() => {
    if (callbackRef.current && condition) {
      callbackRef.current();
    }
  }, [condition]);

  // Run callback periodically when condition is set.
  useEffect(() => {
    if (callbackRef.current && condition) {
      const tick = () => {
        if (callbackRef.current && condition) {
          callbackRef.current();
        }
      };
      const id = setInterval(tick, delay);
      return () => clearInterval(id);
    }
  }, [condition, delay]);
}

export function useRequestAnimationFrame(callback, condition, delay?: number) {
  const callbackRef = useRef<() => void>();

  useEffect(() => {
    callbackRef.current = callback;
  }, [callback]);

  useEffect(() => {
    if (callbackRef.current && condition) {
      let lastMs = 0;
      const tick = (nowMs) => {
        if (callbackRef.current && condition) {
          if (!delay) {
            callbackRef.current();
            requestAnimationFrame(tick);
          } else if (lastMs === 0 || nowMs - lastMs >= delay) {
            lastMs = nowMs;
            callbackRef.current();
            requestAnimationFrame(tick);
          } else {
            requestAnimationFrame(tick);
          }
        }
      };
      requestAnimationFrame(tick);
      return () => (callbackRef.current = undefined);
    }
  }, [condition, delay]);
}
