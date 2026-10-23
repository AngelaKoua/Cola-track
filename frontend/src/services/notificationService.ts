/**
 * API service for notifications.
 */

import { NotificationListResponse, UnreadCountResponse } from '@/types/notification';
import { API_BASE } from '@/lib/config'

const API_URL = `${API_BASE}/api`;

export const notificationService = {
    async getAll(userId: number, skip = 0, limit = 20): Promise<NotificationListResponse> {
        const res = await fetch(
            `${API_URL}/notifications?user_id=${userId}&skip=${skip}&limit=${limit}`
        );
        if (!res.ok) throw new Error('Failed to fetch notifications');
        return res.json();
    },

    async getUnreadCount(userId: number): Promise<number> {
        const res = await fetch(
            `${API_URL}/notifications/unread-count?user_id=${userId}`
        );
        if (!res.ok) throw new Error('Failed to fetch unread count');
        const data: UnreadCountResponse = await res.json();
        return data.count;
    },

    async markAsRead(notificationId: number, userId: number): Promise<void> {
        await fetch(
            `${API_URL}/notifications/${notificationId}/read?user_id=${userId}`,
            { method: 'PATCH' }
        );
    },

    async markAllRead(userId: number): Promise<void> {
        await fetch(
            `${API_URL}/notifications/read-all?user_id=${userId}`,
            { method: 'PATCH' }
        );
    }
};
