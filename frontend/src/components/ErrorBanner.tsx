interface ErrorBannerProps {
  message: string;
}

const ErrorBanner = ({ message }: ErrorBannerProps) => {
  return (
    <div className="error-banner">
      <strong>Something went wrong.</strong>
      <span>{message}</span>
    </div>
  );
};

export default ErrorBanner;
