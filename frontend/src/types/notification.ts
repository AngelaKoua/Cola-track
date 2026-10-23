/**
 * Notification types for the internal notification system.
 */

export type NotificationType = 'ASSIGNATION' | 'DEADLINE' | 'CRITICAL';
export type NotificationPriority = 'LOW' | 'MEDIUM' | 'HIGH' | 'URGENT';

export interface Notification {
    id: number;
    user_id: number;
    incident_id: string;
    type: NotificationType;
    titre: string;
    message: string;
    priority: NotificationPriority;
    is_read: boolean;
    created_at: string;
}

export interface NotificationListResponse {
    total: number;
    unread_count: number;
    data: Notification[];
}

export interface UnreadCountResponse {
    count: number;
}

export interface WebSocketNotificationPayload {
    type: 'notification';
    notification_id: number;
    incident_id: string;
    title: string;
    message: string;
    priority: NotificationPriority;
    notif_type: NotificationType;
    created_at: string;
}
