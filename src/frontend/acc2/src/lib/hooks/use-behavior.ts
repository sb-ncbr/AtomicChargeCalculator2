import { useCallback, useSyncExternalStore } from "react";
import { BehaviorSubject } from "rxjs";

export function useBehavior<T>(s: BehaviorSubject<T>): T;
export function useBehavior<T>(
  s: BehaviorSubject<T> | undefined
): T | undefined {
  const state = useSyncExternalStore(
    useCallback(
      (callback: () => void) => {
        const sub = s?.subscribe(callback);
        return () => sub?.unsubscribe();
      },
      [s]
    ),
    useCallback(() => s?.value, [s])
  );

  return state;
}
