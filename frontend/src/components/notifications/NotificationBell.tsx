'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Bell } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';
import { useNotifications } from '@/hooks/useNotifications';
import { Notification, NotificationPriority } from '@/types/notification';
import { motion, AnimatePresence } from 'framer-motion';

/**
 * Format relative time (e.g. "il y a 5 min")
 */
function timeAgo(dateStr: string): string {
    const now = new Date();
    const date = new Date(dateStr);
    const diffMs = now.getTime() - date.getTime();
    const diffMin = Math.floor(diffMs / 60000);
    const diffH = Math.floor(diffMin / 60);
    const diffD = Math.floor(diffH / 24);

    if (diffMin < 1) return "à l'instant";
    if (diffMin < 60) return `il y a ${diffMin} min`;
    if (diffH < 24) return `il y a ${diffH}h`;
    return `il y a ${diffD}j`;
}

/**
 * Priority-based styling
 */
function getPriorityStyles(priority: NotificationPriority) {
    switch (priority) {
        case 'URGENT':
            return { bg: 'bg-red-50', border: 'border-l-red-600', dot: 'bg-red-500', text: 'text-red-700' };
        case 'HIGH':
            return { bg: 'bg-orange-50', border: 'border-l-orange-500', dot: 'bg-orange-500', text: 'text-orange-700' };
        case 'MEDIUM':
            return { bg: 'bg-yellow-50', border: 'border-l-yellow-500', dot: 'bg-yellow-500', text: 'text-yellow-700' };
        case 'LOW':
        default:
            return { bg: 'bg-gray-50', border: 'border-l-gray-400', dot: 'bg-gray-400', text: 'text-gray-600' };
    }
}

/**
 * Type label for notification
 */
function getTypeLabel(type: string): string {
    switch (type) {
        case 'ASSIGNATION': return 'Assignation';
        case 'DEADLINE': return 'Deadline';
        case 'CRITICAL': return 'Critique';
        default: return type;
    }
}

export function NotificationBell() {
    const { user } = useAuth();
    const userId = user?.userId ?? null;
    const { notifications, unreadCount, markAsRead, markAllRead } = useNotifications(userId);
    const [isOpen, setIsOpen] = useState(false);
    const dropdownRef = useRef<HTMLDivElement>(null);
    const router = useRouter();

    // Close dropdown on outside click
    useEffect(() => {
        const handleClickOutside = (e: MouseEvent) => {
            if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
                setIsOpen(false);
            }
        };
        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    const handleNotificationClick = async (notif: Notification) => {
        if (!notif.is_read) {
            await markAsRead(notif.id);
        }
        setIsOpen(false);
        if (notif.incident_id) {
            router.push(`/dashboard/incidents?viewIncident=${notif.incident_id}`);
        } else {
            router.push(`/dashboard/incidents`);
        }
    };

    // Separate pinned urgent from others
    const urgentNotifs = notifications.filter(n => n.priority === 'URGENT' && !n.is_read);
    const otherNotifs = notifications.filter(n => !(n.priority === 'URGENT' && !n.is_read));

    return (
        <div className="relative" ref={dropdownRef}>
            {/* Bell Button */}
            <button
                onClick={() => setIsOpen(!isOpen)}
                className="relative p-2 rounded-lg hover:bg-gray-100/80 transition-colors focus:outline-none"
            >
                <div className="relative">
                    {/* Glowing pulse behind the bell if unread */}
                    {unreadCount > 0 && (
                        <motion.div
                            animate={{ opacity: [0.3, 0.7, 0.3], scale: [1, 1.2, 1] }}
                            transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
                            className="absolute inset-0 bg-red-400 rounded-full blur-sm"
                        />
                    )}

                    {/* Swinging ringing bell if unread */}
                    <motion.div
                        animate={unreadCount > 0 ? {
                            rotate: [0, -10, 10, -10, 10, -5, 5, 0],
                        } : { rotate: 0 }}
                        transition={unreadCount > 0 ? {
                            duration: 1.5,
                            repeat: Infinity,
                            repeatDelay: 1,
                            ease: "easeInOut"
                        } : {}}
                        className="relative z-10"
                    >
                        <Bell className="h-5 w-5 text-gray-700" />
                    </motion.div>
                </div>

                {unreadCount > 0 && (
                    <motion.span
                        initial={{ scale: 0 }}
                        animate={{ scale: 1 }}
                        className="absolute -top-0.5 -right-0.5 min-w-[18px] h-[18px] flex items-center justify-center px-1 text-[10px] font-bold text-white bg-red-500 rounded-full border-2 border-white z-20 shadow-sm"
                    >
                        {unreadCount > 99 ? '99+' : unreadCount}
                    </motion.span>
                )}
            </button>

            {/* Dropdown */}
            <AnimatePresence>
                {isOpen && (
                    <motion.div
                        initial={{ opacity: 0, y: 10, scale: 0.95 }}
                        animate={{ opacity: 1, y: 0, scale: 1 }}
                        exit={{ opacity: 0, y: 10, scale: 0.95 }}
                        transition={{ duration: 0.2 }}
                        className="absolute right-0 mt-2 w-96 bg-white rounded-xl shadow-2xl border border-gray-100 z-50 origin-top-right overflow-hidden"
                    >
                        {/* Header */}
                        <div className="flex items-center justify-between px-4 py-3 border-b border-gray-100 bg-gray-50/50">
                            <h3 className="text-sm font-semibold text-gray-800">Notifications</h3>
                            <div className="flex items-center gap-2">
                                {unreadCount > 0 && (
                                    <span className="text-xs px-2 py-0.5 bg-red-100 text-red-700 rounded-full font-medium">
                                        {unreadCount} non lue{unreadCount > 1 ? 's' : ''}
                                    </span>
                                )}
                                {unreadCount > 0 && (
                                    <button
                                        onClick={() => markAllRead()}
                                        className="text-xs text-gray-500 hover:text-gray-800 font-medium transition-colors"
                                    >
                                        Tout lire
                                    </button>
                                )}
                            </div>
                        </div>

                        {/* Notification List */}
                        <div className="max-h-[400px] overflow-y-auto">
                            {notifications.length === 0 ? (
                                <div className="px-4 py-8 text-center">
                                    <Bell className="h-8 w-8 text-gray-300 mx-auto mb-2" />
                                    <p className="text-sm text-gray-400">Aucune notification</p>
                                </div>
                            ) : (
                                <>
                                    {/* Pinned urgent notifications */}
                                    {urgentNotifs.length > 0 && (
                                        <div className="bg-red-50/50 border-b border-red-100">
                                            <div className="px-3 py-1.5">
                                                <span className="text-[10px] font-bold text-red-600 uppercase tracking-wider">Urgent</span>
                                            </div>
                                            {urgentNotifs.map(notif => (
                                                <NotificationItem
                                                    key={notif.id}
                                                    notif={notif}
                                                    onClick={handleNotificationClick}
                                                />
                                            ))}
                                        </div>
                                    )}

                                    {/* Other notifications */}
                                    {otherNotifs.map(notif => (
                                        <NotificationItem
                                            key={notif.id}
                                            notif={notif}
                                            onClick={handleNotificationClick}
                                        />
                                    ))}
                                </>
                            )}
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
}

/**
 * Individual notification item
 */
function NotificationItem({
    notif,
    onClick
}: {
    notif: Notification;
    onClick: (n: Notification) => void;
}) {
    const styles = getPriorityStyles(notif.priority);

    return (
        <button
            onClick={() => onClick(notif)}
            className={`w-full text-left px-4 py-3 border-l-4 ${styles.border} hover:bg-gray-50 transition-colors border-b border-gray-50 last:border-b-0 ${!notif.is_read ? styles.bg : 'bg-white opacity-70'}`}
        >
            <div className="flex items-start justify-between gap-2">
                <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-0.5">
                        {!notif.is_read && (
                            <span className={`w-2 h-2 rounded-full ${styles.dot} flex-shrink-0`} />
                        )}
                        <span className={`text-sm font-semibold ${!notif.is_read ? 'text-gray-900' : 'text-gray-500'} truncate`}>
                            {notif.titre}
                        </span>
                    </div>
                    <p className="text-xs text-gray-500 line-clamp-2 mt-0.5">{notif.message}</p>
                    <div className="flex items-center gap-2 mt-1.5">
                        <span className={`text-[10px] px-1.5 py-0.5 rounded font-medium ${styles.text} ${styles.bg}`}>
                            {getTypeLabel(notif.type)}
                        </span>
                        <span className="text-[10px] text-gray-400">{timeAgo(notif.created_at)}</span>
                    </div>
                </div>
            </div>
        </button>
    );
}

export default NotificationBell;
