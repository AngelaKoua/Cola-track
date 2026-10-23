'use client';

/**
 * React hook for managing notifications with WebSocket real-time updates.
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { Notification, WebSocketNotificationPayload } from '@/types/notification';
import { notificationService } from '@/services/notificationService';
import { WS_BASE } from '@/lib/config'


interface UseNotificationsResult {
    notifications: Notification[];
    unreadCount: number;
    isLoading: boolean;
    markAsRead: (notificationId: number) => Promise<void>;
    markAllRead: () => Promise<void>;
    refresh: () => Promise<void>;
}

export function useNotifications(userId: number | null): UseNotificationsResult {
    const [notifications, setNotifications] = useState<Notification[]>([]);
    const [unreadCount, setUnreadCount] = useState(0);
    const [isLoading, setIsLoading] = useState(true);
    const wsRef = useRef<WebSocket | null>(null);

    // Fetch notifications from API
    const refresh = useCallback(async () => {
        if (!userId) return;
        try {
            const data = await notificationService.getAll(userId, 0, 30);
            setNotifications(data.data);
            setUnreadCount(data.unread_count);
        } catch (err) {
            console.error('Failed to fetch notifications:', err);
        } finally {
            setIsLoading(false);
        }
    }, [userId]);

    // Initial load
    useEffect(() => {
        if (userId) {
            refresh();
        } else {
            setIsLoading(false);
        }
    }, [userId, refresh]);

    // WebSocket connection for real-time updates
    useEffect(() => {
        if (!userId) return;

        const connect = () => {
            const ws = new WebSocket(`${WS_BASE}/ws/notifications/${userId}`);

            ws.onopen = () => {
                console.log('[WS] Notification channel connected');
            };

            ws.onmessage = (event) => {
                try {
                    const payload: WebSocketNotificationPayload = JSON.parse(event.data);
                    if (payload.type === 'notification') {
                        // Add to top of list
                        const newNotif: Notification = {
                            id: payload.notification_id,
                            user_id: userId,
                            incident_id: payload.incident_id,
                            type: payload.notif_type,
                            titre: payload.title,
                            message: payload.message,
                            priority: payload.priority,
                            is_read: false,
                            created_at: payload.created_at
                        };
                        setNotifications(prev => [newNotif, ...prev]);
                        setUnreadCount(prev => prev + 1);
                    }
                } catch (err) {
                    console.error('[WS] Parse error:', err);
                }
            };

            ws.onclose = () => {
                console.log('[WS] Disconnected, reconnecting in 5s...');
                setTimeout(connect, 5000);
            };

            ws.onerror = () => {
                ws.close();
            };

            wsRef.current = ws;
        };

        connect();

        return () => {
            wsRef.current?.close();
        };
    }, [userId]);

    const markAsRead = useCallback(async (notificationId: number) => {
        if (!userId) return;
        await notificationService.markAsRead(notificationId, userId);
        setNotifications(prev =>
            prev.map(n => n.id === notificationId ? { ...n, is_read: true } : n)
        );
        setUnreadCount(prev => Math.max(0, prev - 1));
    }, [userId]);

    const markAllRead = useCallback(async () => {
        if (!userId) return;
        await notificationService.markAllRead(userId);
        setNotifications(prev => prev.map(n => ({ ...n, is_read: true })));
        setUnreadCount(0);
    }, [userId]);

    return {
        notifications,
        unreadCount,
        isLoading,
        markAsRead,
        markAllRead,
        refresh
    };
}
