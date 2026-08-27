export function LoadingMessage() {
  return (
    <div className="loading-message" role="status" aria-live="polite">
      <span className="loading-orb" aria-hidden="true" />
      <span>Solving your geometry problem...</span>
    </div>
  );
}
