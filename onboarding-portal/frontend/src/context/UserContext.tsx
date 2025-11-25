import { createContext, useContext, useMemo, ReactNode } from 'react';

type User = {
  id: string;
  name: string;
  roles: string[];
  subscription?: 'free' | 'pro' | 'enterprise';
  featureFlags?: string[];
};

const defaultUser: User = {
  id: 'demo-user',
  name: 'Demo User',
  roles: ['admin'],
  subscription: 'enterprise',
  featureFlags: [],
};

const UserContext = createContext<User>(defaultUser);

export function UserProvider({
  children,
  user,
}: {
  children: ReactNode;
  user?: User;
}) {
  const value = useMemo(() => user || defaultUser, [user]);
  return <UserContext.Provider value={value}>{children}</UserContext.Provider>;
}

export function useUser() {
  return useContext(UserContext);
}

