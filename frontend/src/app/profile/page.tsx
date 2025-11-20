'use client';

import { useAuth } from '@/hooks/useAuth';
import Navbar from '@/components/Navbar';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { User, Mail, Building, Calendar } from 'lucide-react';

export default function ProfilePage() {
  const { user } = useAuth();

  const formatDate = (date: string) => {
    return new Date(date).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      
      <div className="container mx-auto px-4 py-8 max-w-2xl">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900">Profile Settings</h1>
          <p className="text-gray-600 mt-2">Manage your account information</p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Account Information</CardTitle>
            <CardDescription>Your personal details and settings</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="space-y-2">
              <label className="text-sm font-medium flex items-center space-x-2">
                <User className="h-4 w-4 text-gray-500" />
                <span>Full Name</span>
              </label>
              <Input value={user?.name || ''} readOnly className="bg-gray-50" />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium flex items-center space-x-2">
                <Mail className="h-4 w-4 text-gray-500" />
                <span>Email Address</span>
              </label>
              <Input value={user?.email || ''} readOnly className="bg-gray-50" />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium flex items-center space-x-2">
                <Building className="h-4 w-4 text-gray-500" />
                <span>Organization</span>
              </label>
              <Input 
                value={user?.organization || 'Not specified'} 
                readOnly 
                className="bg-gray-50" 
              />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium flex items-center space-x-2">
                <Calendar className="h-4 w-4 text-gray-500" />
                <span>Member Since</span>
              </label>
              <Input 
                value={user?.created_at ? formatDate(user.created_at) : 'N/A'} 
                readOnly 
                className="bg-gray-50" 
              />
            </div>

            <div className="pt-4 space-y-3">
              <Button variant="outline" className="w-full" disabled>
                Update Profile (Coming Soon)
              </Button>
              <Button variant="outline" className="w-full text-red-600 border-red-200 hover:bg-red-50" disabled>
                Change Password (Coming Soon)
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Account Stats */}
        <Card className="mt-6">
          <CardHeader>
            <CardTitle>Account Activity</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-4 text-center">
              <div className="p-4 bg-blue-50 rounded-lg">
                <p className="text-2xl font-bold text-blue-600">-</p>
                <p className="text-sm text-gray-600">Files Uploaded</p>
              </div>
              <div className="p-4 bg-green-50 rounded-lg">
                <p className="text-2xl font-bold text-green-600">-</p>
                <p className="text-sm text-gray-600">Chats Started</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
