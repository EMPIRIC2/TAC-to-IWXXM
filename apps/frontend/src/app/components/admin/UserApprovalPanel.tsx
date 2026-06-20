import { useState, useEffect } from 'react';
import { Button } from '../ui/button';
import { Card } from '../ui/card';
import { Input } from '../ui/input';
import { Loader2, CheckCircle, XCircle, Mail, Calendar, User, Users, Search } from 'lucide-react';
import { toast } from 'sonner';
import { supabase } from '/utils/supabase/client';

interface PendingUser {
  id: string;
  email: string;
  username: string;
  approval_status: 'pending' | 'approved' | 'rejected';
  created_at: string;
}

interface UserApprovalPanelProps {
  accessToken: string;
}

export function UserApprovalPanel({ accessToken: _accessToken }: UserApprovalPanelProps) {
  const [pendingUsers, setPendingUsers] = useState<PendingUser[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [processingUsers, setProcessingUsers] = useState<Set<string>>(new Set());
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    loadPendingUsers();
  }, []);

  const loadPendingUsers = async () => {
    setIsLoading(true);
    try {
      // Query Supabase database directly
      const { data, error } = await supabase
        .from('user_profiles')
        .select('*')
        .eq('approval_status', 'pending')
        .order('created_at', { ascending: false });

      if (error) {
        console.error('Error loading pending users:', error);
        throw error;
      }

      setPendingUsers(data || []);
    } catch (error) {
      console.error('Error loading pending users:', error);
      toast.error('Failed to load pending users');
    } finally {
      setIsLoading(false);
    }
  };

  const handleApprove = async (userId: string, userEmail: string) => {
    setProcessingUsers(prev => new Set(prev).add(userId));
    try {
      // Get current user for approved_by
      const { data: { user } } = await supabase.auth.getUser();
      
      if (!user) {
        throw new Error('Not authenticated');
      }

      // Update approval status in database
      const { error } = await supabase
        .from('user_profiles')
        .update({
          approval_status: 'approved',
          approved_at: new Date().toISOString(),
          approved_by: user.id,
        })
        .eq('id', userId);

      if (error) {
        console.error('Error approving user:', error);
        throw error;
      }

      toast.success(`User ${userEmail} approved successfully!`);
      await loadPendingUsers();
    } catch (error) {
      console.error('Error approving user:', error);
      toast.error('Failed to approve user');
    } finally {
      setProcessingUsers(prev => {
        const newSet = new Set(prev);
        newSet.delete(userId);
        return newSet;
      });
    }
  };

  const handleReject = async (userId: string, userEmail: string) => {
    setProcessingUsers(prev => new Set(prev).add(userId));
    try {
      // Get current user for approved_by
      const { data: { user } } = await supabase.auth.getUser();
      
      if (!user) {
        throw new Error('Not authenticated');
      }

      // Update approval status in database
      const { error } = await supabase
        .from('user_profiles')
        .update({
          approval_status: 'rejected',
          approved_at: new Date().toISOString(),
          approved_by: user.id,
        })
        .eq('id', userId);

      if (error) {
        console.error('Error rejecting user:', error);
        throw error;
      }

      toast.success(`User ${userEmail} rejected`);
      await loadPendingUsers();
    } catch (error) {
      console.error('Error rejecting user:', error);
      toast.error('Failed to reject user');
    } finally {
      setProcessingUsers(prev => {
        const newSet = new Set(prev);
        newSet.delete(userId);
        return newSet;
      });
    }
  };

  const filteredUsers = pendingUsers.filter(user =>
    user.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
    user.username.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-semibold text-gray-900 dark:text-white">
          Pending User Approvals
        </h2>
        <Button
          onClick={loadPendingUsers}
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

      {/* Search */}
      <div className="mb-6">
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

      {isLoading && pendingUsers.length === 0 ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-gray-400" />
        </div>
      ) : filteredUsers.length === 0 ? (
        <div className="text-center py-12">
          <Users className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600 dark:text-gray-400">
            {searchTerm ? 'No users match your search' : 'No pending approvals'}
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {filteredUsers.map((user) => {
            const isProcessing = processingUsers.has(user.id);
            
            return (
              <Card key={user.id} className="p-4 dark:bg-gray-750 dark:border-gray-700">
                <div className="flex items-center justify-between gap-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <User className="w-4 h-4 text-gray-500" />
                      <span className="font-semibold text-gray-900 dark:text-white">
                        {user.username}
                      </span>
                    </div>
                    <div className="flex items-center gap-2 mb-1">
                      <Mail className="w-4 h-4 text-gray-500" />
                      <span className="text-sm text-gray-600 dark:text-gray-400">
                        {user.email}
                      </span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Calendar className="w-4 h-4 text-gray-500" />
                      <span className="text-sm text-gray-600 dark:text-gray-400">
                        Requested: {new Date(user.created_at).toLocaleString()}
                      </span>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <Button
                      onClick={() => handleApprove(user.id, user.email)}
                      disabled={isProcessing}
                      className="bg-green-500 hover:bg-green-600 text-white dark:bg-green-600 dark:hover:bg-green-700"
                    >
                      {isProcessing ? (
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      ) : (
                        <CheckCircle className="w-4 h-4 mr-2" />
                      )}
                      Approve
                    </Button>
                    <Button
                      onClick={() => handleReject(user.id, user.email)}
                      disabled={isProcessing}
                      className="bg-red-500 hover:bg-red-600 text-white dark:bg-red-600 dark:hover:bg-red-700"
                    >
                      {isProcessing ? (
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      ) : (
                        <XCircle className="w-4 h-4 mr-2" />
                      )}
                      Reject
                    </Button>
                  </div>
                </div>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}