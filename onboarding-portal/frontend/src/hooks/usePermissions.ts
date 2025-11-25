import { useMemo } from 'react';
import { useUser } from '@/context/UserContext';

const FEATURE_FLAG = import.meta.env.VITE_FEATURE_QUICK_ASSESS ?? 'true';

export function usePermissions() {
  const user = useUser();

  const canUseQuickAssess = useMemo(() => {
    const enabled = FEATURE_FLAG !== 'false';
    if (!enabled) return false;

    const roleBased =
      user.roles.includes('quick_assess') ||
      user.roles.includes('admin') ||
      user.roles.includes('architect');

    const planBased = user.subscription === 'enterprise' || user.subscription === 'pro';
    const betaFlag = user.featureFlags?.includes('quick_assess_beta');

    return roleBased || planBased || betaFlag;
  }, [user]);

  return {
    user,
    canUseQuickAssess,
  };
}

