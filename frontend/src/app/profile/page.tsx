'use client';

import React, { useState, useEffect } from 'react';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { 
  UserIcon, 
  MailIcon, 
  PhoneIcon, 
  MapPinIcon,
  BriefcaseIcon,
  CalendarIcon,
  CameraIcon,
  CheckCircleIcon,
  ShieldCheckIcon
} from 'lucide-react';

interface UserProfile {
  name: string;
  email: string;
  phone: string;
  role: string;
  department: string;
  location: string;
  joinDate: string;
  avatar: string;
  bio: string;
  permissions: string[];
}

const ProfilePage = () => {
  const [isEditing, setIsEditing] = useState(false);
  const [loading, setLoading] = useState(true);
  const [profile, setProfile] = useState<UserProfile>({
    name: '',
    email: '',
    phone: '',
    role: '',
    department: '',
    location: '',
    joinDate: '',
    avatar: '/api/placeholder/150/150',
    bio: '',
    permissions: []
  });

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      const response = await fetch('/api/proxy/v1/profile');
      if (response.ok) {
        const data = await response.json();
        setProfile({
          name: data.name || '',
          email: data.email || '',
          phone: data.phone || '',
          role: data.role || '',
          department: data.department || '',
          location: data.location || '',
          joinDate: data.created_at || '',
          avatar: data.avatar_url || '/api/placeholder/150/150',
          bio: data.bio || '',
          permissions: data.permissions || []
        });
      }
    } catch (error) {
      console.error('Error fetching profile:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('it-IT', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const handleSave = async () => {
    try {
      const response = await fetch('/api/proxy/v1/profile', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          name: profile.name,
          department: profile.department,
          phone: profile.phone,
          location: profile.location,
          bio: profile.bio
        })
      });
      
      if (response.ok) {
        setIsEditing(false);
        alert('Profile updated successfully!');
      } else {
        alert('Failed to update profile');
      }
    } catch (error) {
      console.error('Error saving profile:', error);
      alert('Error saving profile');
    }
  };

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex items-center justify-center h-64">
          <div className="animate-pulse text-gray-500">Loading profile...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100">
          User Profile
        </h1>
        <p className="text-gray-600 dark:text-gray-400 mt-2">
          Manage your personal information and preferences
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Profile Card */}
        <Card className="p-6 lg:col-span-1">
          <div className="text-center">
            <div className="relative inline-block">
              <div className="w-32 h-32 mx-auto rounded-full bg-gradient-to-br from-blue-400 to-blue-600 flex items-center justify-center text-white text-4xl font-bold">
                {profile.name.split(' ').map(n => n[0]).join('')}
              </div>
              <button className="absolute bottom-0 right-0 bg-blue-500 text-white p-2 rounded-full hover:bg-blue-600 transition-colors">
                <CameraIcon className="h-4 w-4" />
              </button>
            </div>
            
            <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mt-4">
              {profile.name}
            </h2>
            <p className="text-gray-600 dark:text-gray-400">{profile.role}</p>
            
            <div className="mt-6 space-y-3">
              <div className="flex items-center justify-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                <BriefcaseIcon className="h-4 w-4" />
                {profile.department}
              </div>
              <div className="flex items-center justify-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                <MapPinIcon className="h-4 w-4" />
                {profile.location}
              </div>
              <div className="flex items-center justify-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                <CalendarIcon className="h-4 w-4" />
                Joined {formatDate(profile.joinDate)}
              </div>
            </div>
          </div>
        </Card>

        {/* Information Card */}
        <Card className="p-6 lg:col-span-2">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
              Personal Information
            </h3>
            <Button
              onClick={() => isEditing ? handleSave() : setIsEditing(true)}
              variant="primary"
            >
              {isEditing ? 'Save Changes' : 'Edit Profile'}
            </Button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Full Name
              </label>
              {isEditing ? (
                <input
                  type="text"
                  value={profile.name}
                  onChange={(e) => setProfile({ ...profile, name: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-800"
                />
              ) : (
                <p className="text-gray-900 dark:text-gray-100">{profile.name}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Email Address
              </label>
              {isEditing ? (
                <input
                  type="email"
                  value={profile.email}
                  onChange={(e) => setProfile({ ...profile, email: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-800"
                />
              ) : (
                <p className="text-gray-900 dark:text-gray-100">{profile.email}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Phone Number
              </label>
              {isEditing ? (
                <input
                  type="tel"
                  value={profile.phone}
                  onChange={(e) => setProfile({ ...profile, phone: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-800"
                />
              ) : (
                <p className="text-gray-900 dark:text-gray-100">{profile.phone}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Department
              </label>
              {isEditing ? (
                <select
                  value={profile.department}
                  onChange={(e) => setProfile({ ...profile, department: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-800"
                >
                  <option>Operations & Maintenance</option>
                  <option>Engineering</option>
                  <option>Quality Control</option>
                  <option>Administration</option>
                </select>
              ) : (
                <p className="text-gray-900 dark:text-gray-100">{profile.department}</p>
              )}
            </div>
          </div>

          <div className="mt-6">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Bio
            </label>
            {isEditing ? (
              <textarea
                value={profile.bio}
                onChange={(e) => setProfile({ ...profile, bio: e.target.value })}
                rows={4}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-800"
              />
            ) : (
              <p className="text-gray-900 dark:text-gray-100">{profile.bio}</p>
            )}
          </div>
        </Card>

        {/* Security & Permissions */}
        <Card className="p-6 lg:col-span-3">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-6">
            Security & Permissions
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-medium text-gray-900 dark:text-gray-100 mb-4 flex items-center gap-2">
                <ShieldCheckIcon className="h-5 w-5 text-green-600" />
                Account Security
              </h4>
              <div className="space-y-3">
                <div className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                  <span className="text-sm text-gray-700 dark:text-gray-300">Two-Factor Authentication</span>
                  <span className="text-sm font-medium text-green-600">Enabled</span>
                </div>
                <div className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                  <span className="text-sm text-gray-700 dark:text-gray-300">Last Password Change</span>
                  <span className="text-sm text-gray-600 dark:text-gray-400">45 days ago</span>
                </div>
                <Button variant="secondary" className="w-full">
                  Change Password
                </Button>
              </div>
            </div>

            <div>
              <h4 className="font-medium text-gray-900 dark:text-gray-100 mb-4">
                System Permissions
              </h4>
              <div className="space-y-2">
                {profile.permissions.map((permission, idx) => (
                  <div key={idx} className="flex items-center gap-2 text-sm">
                    <CheckCircleIcon className="h-4 w-4 text-green-500" />
                    <span className="text-gray-700 dark:text-gray-300">{permission}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </Card>

        {/* Activity Log */}
        <Card className="p-6 lg:col-span-3">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-6">
            Recent Activity
          </h3>
          <div className="space-y-3">
            {[
              { action: 'Logged in', time: '2 hours ago', icon: UserIcon },
              { action: 'Generated monthly report', time: '1 day ago', icon: BriefcaseIcon },
              { action: 'Updated pump settings', time: '3 days ago', icon: CheckCircleIcon },
              { action: 'Modified alert thresholds', time: '1 week ago', icon: ShieldCheckIcon }
            ].map((activity, idx) => (
              <div key={idx} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                <div className="flex items-center gap-3">
                  <activity.icon className="h-4 w-4 text-gray-500" />
                  <span className="text-sm text-gray-700 dark:text-gray-300">{activity.action}</span>
                </div>
                <span className="text-sm text-gray-500 dark:text-gray-400">{activity.time}</span>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
};

export default ProfilePage; 