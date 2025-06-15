import * as React from 'react'; // Changed import style
import { Component, ErrorInfo, ReactNode } from 'react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode; // Optional custom fallback UI
}

interface State {
  hasError: boolean;
  error?: Error;
  errorInfo?: ErrorInfo;
}

class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    // Update state so the next render will show the fallback UI.
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // You can also log the error to an error reporting service
    console.error("Uncaught error:", error, errorInfo);
    this.setState({ errorInfo });
    // Example: logErrorToMyService(error, errorInfo);
  }

  handleResetError = () => {
    // Attempt to reset the error state. This might not always work if the underlying issue persists.
    // A more robust solution might involve re-initializing parts of the app or navigating away.
    this.setState({ hasError: false, error: undefined, errorInfo: undefined });
    // Optionally, could try to reload the page or a specific component
    // window.location.reload(); // Or a more targeted reset
  };

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }
      // Default fallback UI
      return (
        <div className="p-4 m-4 bg-red-100 border border-red-400 text-red-700 rounded text-center">
          <h2 className="text-lg font-semibold mb-2">Oops! Something went wrong.</h2>
          <p className="mb-2">
            We're sorry for the inconvenience. Please try refreshing the page.
          </p>
          {/* Vite uses import.meta.env.DEV for development mode check */}
          {import.meta.env.DEV && this.state.error && (
            <details className="text-left text-xs bg-red-50 p-2 rounded mt-2">
              <summary>Error Details (Development Only)</summary>
              <pre className="whitespace-pre-wrap">
                {this.state.error.toString()}
                {this.state.errorInfo && `\nComponent Stack:\n${this.state.errorInfo.componentStack}`}
              </pre>
            </details>
          )}
          <button
            onClick={() => window.location.reload()}
            className="mt-4 px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600 transition-colors"
          >
            Refresh Page
          </button>
          {/* 
          // Optional: A button to try resetting the component's error state without a full reload.
          // This is less reliable if the error source is persistent.
          <button
            onClick={this.handleResetError}
            className="ml-2 mt-4 px-4 py-2 bg-yellow-500 text-white rounded hover:bg-yellow-600 transition-colors"
          >
            Try to Recover
          </button>
          */}
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
