import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../api/client';
import './Dashboard.css';

export default function Dashboard() {
    const [bots, setBots] = useState([]);
    const [conversations, setConversations] = useState([]);
    const [loadingBots, setLoadingBots] = useState(true);
    const [loadingConvs, setLoadingConvs] = useState(true);

    useEffect(() => {
        fetchBots();
        fetchConversations();
    }, []);

    const fetchBots = async () => {
        try {
            const response = await api.get('/api/bots/');
            setBots(response.data);
        } catch (error) {
            console.error('Failed to fetch bots:', error);
        } finally {
            setLoadingBots(false);
        }
    };

    const fetchConversations = async () => {
        try {
            const response = await api.get('/api/conversations/');
            setConversations(response.data);
        } catch (error) {
            console.error('Failed to fetch conversations:', error);
        } finally {
            setLoadingConvs(false);
        }
    };

    const toggleBot = async (botId) => {
        try {
            await api.put(`/api/bots/${botId}/toggle`);
            fetchBots();
        } catch (error) {
            console.error('Failed to toggle bot:', error);
        }
    };

    return (
        <div className="page">
            <div className="container">
                <div className="dashboard-header animate-fade-in">
                    <div>
                        <h1 className="dashboard-title">Dashboard</h1>
                        <p className="dashboard-subtitle">Manage your bots and conversations</p>
                    </div>
                    <Link to="/bots/add" className="btn btn-primary">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <line x1="12" y1="5" x2="12" y2="19" />
                            <line x1="5" y1="12" x2="19" y2="12" />
                        </svg>
                        Add Bot
                    </Link>
                </div>

                {/* Bots Section */}
                <section className="dashboard-section animate-fade-in">
                    <h2 className="section-title">Your Bots</h2>

                    {loadingBots ? (
                        <div className="loading-state">
                            <div className="spinner" />
                        </div>
                    ) : bots.length === 0 ? (
                        <div className="empty-state card">
                            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                                <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
                                <path d="M7 11V7a5 5 0 0 1 10 0v4" />
                            </svg>
                            <h3>No bots yet</h3>
                            <p>Add your first Telegram bot to get started</p>
                            <Link to="/bots/add" className="btn btn-primary">Add Bot</Link>
                        </div>
                    ) : (
                        <div className="grid grid-3">
                            {bots.map((bot) => (
                                <div key={bot.id} className="card bot-card">
                                    <div className="bot-header">
                                        <div className="bot-avatar">
                                            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                                <circle cx="12" cy="12" r="10" />
                                                <path d="M8 14s1.5 2 4 2 4-2 4-2" />
                                                <line x1="9" y1="9" x2="9.01" y2="9" />
                                                <line x1="15" y1="9" x2="15.01" y2="9" />
                                            </svg>
                                        </div>
                                        <div className="bot-info">
                                            <h3 className="bot-name">{bot.name}</h3>
                                            {bot.bot_username && (
                                                <span className="bot-username">@{bot.bot_username}</span>
                                            )}
                                        </div>
                                    </div>

                                    <div className="bot-stats">
                                        <div className="stat">
                                            <span className="stat-value">{bot.conversations_count}</span>
                                            <span className="stat-label">Conversations</span>
                                        </div>
                                    </div>

                                    <div className="bot-footer">
                                        <span className={`badge ${bot.is_active ? 'badge-success' : 'badge-neutral'}`}>
                                            {bot.is_active ? 'Active' : 'Inactive'}
                                        </span>
                                        <label className="toggle">
                                            <input
                                                type="checkbox"
                                                checked={bot.is_active}
                                                onChange={() => toggleBot(bot.id)}
                                            />
                                            <span className="toggle-slider" />
                                        </label>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </section>

                {/* Conversations Section */}
                <section className="dashboard-section animate-fade-in">
                    <h2 className="section-title">Recent Conversations</h2>

                    {loadingConvs ? (
                        <div className="loading-state">
                            <div className="spinner" />
                        </div>
                    ) : conversations.length === 0 ? (
                        <div className="empty-state card">
                            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
                            </svg>
                            <h3>No conversations yet</h3>
                            <p>When customers message your bot, conversations will appear here</p>
                        </div>
                    ) : (
                        <div className="conversations-list">
                            {conversations.map((conv) => (
                                <Link key={conv.id} to={`/conversations/${conv.id}`} className="conversation-item card">
                                    <div className="conversation-avatar">
                                        {conv.telegram_first_name?.[0] || conv.telegram_username?.[0] || '?'}
                                    </div>
                                    <div className="conversation-info">
                                        <div className="conversation-header">
                                            <span className="conversation-name">
                                                {conv.telegram_first_name || conv.telegram_username || 'Unknown'}
                                            </span>
                                            <span className="conversation-time">
                                                {conv.last_message_at
                                                    ? new Date(conv.last_message_at).toLocaleString('ru-RU', {
                                                        day: 'numeric',
                                                        month: 'short',
                                                        hour: '2-digit',
                                                        minute: '2-digit',
                                                    })
                                                    : ''}
                                            </span>
                                        </div>
                                        <p className="conversation-preview">{conv.last_message || 'No messages'}</p>
                                    </div>
                                    <div className="conversation-status">
                                        <span className={`badge ${conv.is_ai_controlled ? 'badge-success' : 'badge-warning'}`}>
                                            {conv.is_ai_controlled ? 'AI' : 'Manual'}
                                        </span>
                                    </div>
                                </Link>
                            ))}
                        </div>
                    )}
                </section>
            </div>
        </div>
    );
}
