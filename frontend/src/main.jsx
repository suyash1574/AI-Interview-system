import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { ClerkProvider } from '@clerk/clerk-react';
import App from './App.jsx';
import './index.css';

const clerkPubKey = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY;

function Root() {
  const content = (
    <BrowserRouter>
      <App />
    </BrowserRouter>
  );

  if (clerkPubKey && !clerkPubKey.includes('placeholder')) {
    return <ClerkProvider publishableKey={clerkPubKey}>{content}</ClerkProvider>;
  }

  return content;
}

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <Root />
  </React.StrictMode>,
);
