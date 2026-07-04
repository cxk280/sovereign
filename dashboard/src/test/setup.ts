import '@testing-library/jest-dom/vitest';

// jsdom has no ResizeObserver; the charts use it via a width hook.
class ResizeObserverStub {
  observe() {}
  unobserve() {}
  disconnect() {}
}
globalThis.ResizeObserver = ResizeObserverStub as unknown as typeof ResizeObserver;
