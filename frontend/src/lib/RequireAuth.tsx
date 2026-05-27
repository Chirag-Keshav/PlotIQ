import { useAuth, useUser, RedirectToSignIn } from "@clerk/clerk-react";
import React from "react";

export function RequireAuth({ children }: { children: React.ReactNode }) {
  const { isSignedIn, isLoaded } = useAuth();

  if (!isLoaded) {
    return <div>Loading...</div>;
  }

  if (!isSignedIn) {
    return <RedirectToSignIn />;
  }

  return <>{children}</>;
}

export function RequireAdmin({ children }: { children: React.ReactNode }) {
  const { isSignedIn, isLoaded } = useAuth();
  const { user } = useUser();

  if (!isLoaded) {
    return <div>Loading...</div>;
  }

  if (!isSignedIn) {
    return <RedirectToSignIn />;
  }

  // Check if user has admin role in publicMetadata
  const isAdmin = user?.publicMetadata?.role === "admin";
  
  if (!isAdmin) {
    return <div>Unauthorized: Admin access required.</div>;
  }

  return <>{children}</>;
}
