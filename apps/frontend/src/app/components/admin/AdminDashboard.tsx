import { useState } from 'react';
import { Button } from '../ui/button';
import { Card } from '../ui/card';
import { ThemeToggle } from '../ThemeToggle';
import { UserApprovalPanel } from './UserApprovalPanel';
import { SystemSettingsPanel } from './SystemSettingsPanel';
import { MonitoringPanel } from './MonitoringPanel';
import { Users, Settings, Activity, LogOut, FileText, ChevronDown } from 'lucide-react';
import { signOutWithScope } from '/utils/supabase/logout';

interface AdminDashboardProps {
  onLogout: () => void;
  userEmail: string;
  accessToken: string;
  onSwitchToConverter?: () => void;
}

type AdminPanel = 'approval' | 'settings' | 'monitoring';

export function AdminDashboard({ onLogout, userEmail, accessToken, onSwitchToConverter }: AdminDashboardProps) {
  const [activePanel, setActivePanel] = useState<AdminPanel>('approval');
  const [isLogoutMenuOpen, setIsLogoutMenuOpen] = useState(false);

  console.log(`🔐 AdminDashboard mounted for user: ${userEmail}`, { 
    hasAccessToken: !!accessToken,
    accessTokenPrefix: accessToken?.substring(0, 20) + '...'
  });

  // Log when render happens
  console.log(`🎨 AdminDashboard rendering with activePanel=${activePanel}`);

  const handleLogoutWithScope = async (scope: 'global' | 'local' | 'others') => {
    const success = await signOutWithScope(scope);
    if (success) {
      setIsLogoutMenuOpen(false);
      setTimeout(() => {
        onLogout();
      }, 500);
    }
  };

  const panels = [
    {
      id: 'approval' as AdminPanel,
      title: 'User Approvals',
      description: 'Review and approve pending user registrations',
      icon: Users,
      color: 'bg-blue-500 dark:bg-blue-600',
    },
    {
      id: 'settings' as AdminPanel,
      title: 'System Settings',
      description: 'Manage default values and system configuration',
      icon: Settings,
      color: 'bg-green-500 dark:bg-green-600',
    },
    {
      id: 'monitoring' as AdminPanel,
      title: 'System Monitoring',
      description: 'View users, database status, and activity',
      icon: Activity,
      color: 'bg-purple-500 dark:bg-purple-600',
    },
  ];
  
  console.log(`✅ AdminDashboard panels initialized successfully (${panels.length} panels)`);
  console.log(`   Panel icons: Users=${typeof Users}, Settings=${typeof Settings}, Activity=${typeof Activity}`);

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8 px-4 transition-colors">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-3xl font-semibold text-gray-900 dark:text-white">
                Admin Dashboard
              </h1>
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                Logged in as: {userEmail}
              </p>
            </div>
            <div className="flex items-center gap-3">
              {onSwitchToConverter && (
                <Button
                  onClick={onSwitchToConverter}
                  variant="outline"
                  className="bg-blue-600 text-white hover:bg-blue-700 dark:bg-blue-700 dark:hover:bg-blue-800 border-0 focus:ring-2 focus:ring-blue-500"
                  aria-label="Switch to file converter"
                >
                  <FileText className="w-4 h-4 mr-2" />
                  File Converter
                </Button>
              )}
              <div className="flex items-center gap-2">
                <span className="text-sm text-gray-600 dark:text-gray-400">Theme</span>
                <ThemeToggle />
              </div>
              
              {/* Logout Menu */}
              <div className="relative">
                <Button
                  variant="outline"
                  className="bg-red-500 text-white hover:bg-red-600 dark:bg-red-600 dark:hover:bg-red-700 border-0"
                  onClick={() => setIsLogoutMenuOpen(!isLogoutMenuOpen)}
                  aria-label="Logout options"
                >
                  <LogOut className="w-4 h-4 mr-2" aria-hidden="true" />
                  Logout
                  <ChevronDown className="w-4 h-4 ml-1" aria-hidden="true" />
                </Button>
                
                {isLogoutMenuOpen && (
                  <div className="absolute right-0 mt-2 w-48 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-md shadow-lg z-10">
                    <div className="p-3 space-y-2">
                      <p className="text-xs font-semibold text-gray-500 dark:text-gray-400 px-2 py-1">Sign out scope:</p>
                      
                      <button
                        onClick={() => handleLogoutWithScope('local')}
                        className="w-full text-left px-3 py-2 rounded-md text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                        aria-label="Sign out from this device only"
                      >
                        <div className="font-medium">This Device</div>
                        <div className="text-xs text-gray-500 dark:text-gray-400">Only this session</div>
                      </button>
                      
                      <button
                        onClick={() => handleLogoutWithScope('global')}
                        className="w-full text-left px-3 py-2 rounded-md text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                        aria-label="Sign out from all devices"
                      >
                        <div className="font-medium">All Devices</div>
                        <div className="text-xs text-gray-500 dark:text-gray-400">Every logged-in session</div>
                      </button>
                      
                      <button
                        onClick={() => handleLogoutWithScope('others')}
                        className="w-full text-left px-3 py-2 rounded-md text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                        aria-label="Sign out from other devices"
                      >
                        <div className="font-medium">Other Devices</div>
                        <div className="text-xs text-gray-500 dark:text-gray-400">Keep this session active</div>
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Panel Selection Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          {panels.map((panel) => {
            const Icon = panel.icon;
            const isActive = activePanel === panel.id;
            
            return (
              <Card
                key={panel.id}
                className={`p-6 cursor-pointer transition-all hover:shadow-lg ${
                  isActive 
                    ? 'ring-2 ring-blue-500 dark:ring-blue-400 bg-blue-50 dark:bg-blue-950' 
                    : 'bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-750'
                }`}
                onClick={() => setActivePanel(panel.id)}
              >
                <div className="flex items-start gap-4">
                  <div className={`p-3 rounded-lg ${panel.color}`}>
                    <Icon className="w-6 h-6 text-white" />
                  </div>
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-1">
                      {panel.title}
                    </h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      {panel.description}
                    </p>
                  </div>
                </div>
              </Card>
            );
          })}
        </div>

        {/* Active Panel Content */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
          {activePanel === 'approval' && (
            <UserApprovalPanel accessToken={accessToken} />
          )}
          {activePanel === 'settings' && (
            <SystemSettingsPanel accessToken={accessToken} />
          )}
          {activePanel === 'monitoring' && (
            <MonitoringPanel accessToken={accessToken} />
          )}
        </div>
      </div>
    </div>
  );
}