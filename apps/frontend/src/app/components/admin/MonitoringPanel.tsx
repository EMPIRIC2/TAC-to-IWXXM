import { useState, useEffect, useCallback } from 'react';
import { Button } from '../ui/button';
import { Card } from '../ui/card';
import { Input } from '../ui/input';
import { Loader2, Users, Search, CheckCircle, XCircle, Clock, Shield } from 'lucide-react';
import { toast } from 'sonner';
import { projectId } from '/utils/supabase/info';

interface UserInfo {
  user_id: string;
  email: string;
  username: string;
  approval_status: 'pending' | 'approved' | 'rejected';
  is_admin: boolean;
  created_at: string;
  approved_at?: string;
  last_login?: string;
}

interface DatabaseStats {
  totalUsers: number;
  pendingUsers: number;
  approvedUsers: number;
  rejectedUsers: number;
  adminUsers: number;
  totalConversions: number;
  totalStorageUsed: string;
}

interface MonitoringPanelProps {
  accessToken: string;
}

export function MonitoringPanel({ accessToken }: MonitoringPanelProps) {
  const [users, setUsers] = useState<UserInfo[]>([]);
  const [stats, setStats] = useState<DatabaseStats | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState<'all' | 'pending' | 'approved' | 'rejected'>('all');

  const loadMonitoringData = useCallback(async () => {
    setIsLoading(true);
    try {
      const [usersResponse, statsResponse] = await Promise.all([
        fetch(
          `https://${projectId}.supabase.co/functions/v1/make-server-2e3cda33/admin/all-users`,
          {
            headers: {
              'Authorization': `Bearer ${accessToken}`,
            },
          }
        ),
        fetch(
          `https://${projectId}.supabase.co/functions/v1/make-server-2e3cda33/admin/stats`,
          {
            headers: {
              'Authorization': `Bearer ${accessToken}`,
            },
          }
        ),
      ]);

      if (!usersResponse.ok || !statsResponse.ok) {
        throw new Error('Failed to load monitoring data');
      }

      const usersData = await usersResponse.json();
      const statsData = await statsResponse.json();

      setUsers(usersData.users || []);
      setStats(statsData.stats || null);
    } catch (error) {
      console.error('Error loading monitoring data:', error);
      toast.error('Failed to load monitoring data');
    } finally {
      setIsLoading(false);
    }
  }, [accessToken]);

  useEffect(() => {
    loadMonitoringData();
  }, [loadMonitoringData]);

  const toggleAdminStatus = async (userId: string, currentStatus: boolean) => {
    try {
      const response = await fetch(
        `https://${projectId}.supabase.co/functions/v1/make-server-2e3cda33/admin/toggle-admin`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${accessToken}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ userId, isAdmin: !currentStatus }),
        }
      );

      if (!response.ok) {
        throw new Error('Failed to toggle admin status');
      }

      toast.success(`Admin status ${!currentStatus ? 'granted' : 'revoked'}`);
      await loadMonitoringData();
    } catch (error) {
      console.error('Error toggling admin status:', error);
      toast.error('Failed to toggle admin status');
    }
  };

  const filteredUsers = users.filter(user => {
    const matchesSearch = 
      user.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
      user.username.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesFilter = 
      filterStatus === 'all' || user.approval_status === filterStatus;
    
    return matchesSearch && matchesFilter;
  });

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-semibold text-gray-900 dark:text-white">
          System Monitoring
        </h2>
        <Button
          onClick={loadMonitoringData}
          disabled={isLoading}
          variant="outline"
          className="dark:bg-gray-700 dark:text-white"
        >
          {isLoading ? (
            <Loader2 className="w-4 h-4 mr-2 animate-spin" />
          ) : null}
          Refresh
        </Button>
      </div>

      {/* Statistics Cards */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <Card className="p-4 dark:bg-gray-750 dark:border-gray-700">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-blue-100 dark:bg-blue-900 rounded-lg">
                <Users className="w-6 h-6 text-blue-600 dark:text-blue-300" />
              </div>
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Total Users</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {stats.totalUsers}
                </p>
              </div>
            </div>
          </Card>

          <Card className="p-4 dark:bg-gray-750 dark:border-gray-700">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-green-100 dark:bg-green-900 rounded-lg">
                <CheckCircle className="w-6 h-6 text-green-600 dark:text-green-300" />
              </div>
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Approved</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {stats.approvedUsers}
                </p>
              </div>
            </div>
          </Card>

          <Card className="p-4 dark:bg-gray-750 dark:border-gray-700">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-yellow-100 dark:bg-yellow-900 rounded-lg">
                <Clock className="w-6 h-6 text-yellow-600 dark:text-yellow-300" />
              </div>
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Pending</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {stats.pendingUsers}
                </p>
              </div>
            </div>
          </Card>

          <Card className="p-4 dark:bg-gray-750 dark:border-gray-700">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-purple-100 dark:bg-purple-900 rounded-lg">
                <Shield className="w-6 h-6 text-purple-600 dark:text-purple-300" />
              </div>
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Admins</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {stats.adminUsers}
                </p>
              </div>
            </div>
          </Card>
        </div>
      )}

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4 mb-6">
        <div className="flex-1">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
            <Input
              type="text"
              placeholder="Search by email or username..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 dark:bg-gray-700 dark:text-white dark:border-gray-600"
            />
          </div>
        </div>
        <div className="flex gap-2">
          {(['all', 'pending', 'approved', 'rejected'] as const).map((status) => (
            <Button
              key={status}
              onClick={() => setFilterStatus(status)}
              variant={filterStatus === status ? 'default' : 'outline'}
              className={filterStatus === status 
                ? 'bg-blue-500 text-white' 
                : 'dark:bg-gray-700 dark:text-white'
              }
            >
              {status.charAt(0).toUpperCase() + status.slice(1)}
            </Button>
          ))}
        </div>
      </div>

      {/* Users Table */}
      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-gray-400" />
        </div>
      ) : filteredUsers.length === 0 ? (
        <div className="text-center py-12">
          <Users className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600 dark:text-gray-400">
            {searchTerm || filterStatus !== 'all' ? 'No users match your filters' : 'No users found'}
          </p>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-100 dark:bg-gray-750">
              <tr>
                <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900 dark:text-white">
                  User
                </th>
                <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900 dark:text-white">
                  Status
                </th>
                <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900 dark:text-white">
                  Role
                </th>
                <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900 dark:text-white">
                  Created
                </th>
                <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900 dark:text-white">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
              {filteredUsers.map((user) => (
                <tr key={user.user_id} className="bg-white dark:bg-gray-800">
                  <td className="px-4 py-3">
                    <div>
                      <p className="font-medium text-gray-900 dark:text-white">
                        {user.username}
                      </p>
                      <p className="text-sm text-gray-500 dark:text-gray-400">
                        {user.email}
                      </p>
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    <span
                      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        user.approval_status === 'approved'
                          ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                          : user.approval_status === 'pending'
                          ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
                          : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                      }`}
                    >
                      {user.approval_status === 'approved' ? (
                        <CheckCircle className="w-3 h-3 mr-1" />
                      ) : user.approval_status === 'pending' ? (
                        <Clock className="w-3 h-3 mr-1" />
                      ) : (
                        <XCircle className="w-3 h-3 mr-1" />
                      )}
                      {user.approval_status}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    {user.is_admin ? (
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200">
                        <Shield className="w-3 h-3 mr-1" />
                        Admin
                      </span>
                    ) : (
                      <span className="text-sm text-gray-500 dark:text-gray-400">User</span>
                    )}
                  </td>
                  <td className="px-4 py-3">
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      {new Date(user.created_at).toLocaleDateString()}
                    </p>
                  </td>
                  <td className="px-4 py-3">
                    <Button
                      onClick={() => toggleAdminStatus(user.user_id, user.is_admin)}
                      variant="outline"
                      size="sm"
                      className="dark:bg-gray-700 dark:text-white"
                    >
                      {user.is_admin ? 'Revoke Admin' : 'Grant Admin'}
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
