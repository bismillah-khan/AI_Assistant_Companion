interface LoadingDotsProps {
  label?: string;
}

const LoadingDots = ({ label }: LoadingDotsProps) => {
  return (
    <div className="loading-dots">
      {label && <span className="loading-label">{label}</span>}
      <span className="dot" />
      <span className="dot" />
      <span className="dot" />
    </div>
  );
};

export default LoadingDots;
