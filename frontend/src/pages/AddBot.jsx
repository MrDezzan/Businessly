import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api/client';
import { sanitize } from '../api/client';
import './AddBot.css';

export default function AddBot() {
    const [token, setToken] = useState('');
    const [name, setName] = useState('');
    const [description, setDescription] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            await api.post('/api/bots/', {
                token: token.trim(),
                name: sanitize(name),
                business_description: sanitize(description),
            });
            navigate('/dashboard');
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to add bot. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="page">
            <div className="container">
                <div className="add-bot-container animate-fade-in">
                    <div className="add-bot-header">
                        <h1 className="add-bot-title">Add Telegram Bot</h1>
                        <p className="add-bot-subtitle">Connect your Telegram bot to Businessly</p>
                    </div>

                    <div className="add-bot-instructions card">
                        <h3>How to get a bot token:</h3>
                        <ol>
                            <li>Open <strong>@BotFather</strong> in Telegram</li>
                            <li>Send <code>/newbot</code> command</li>
                            <li>Follow the instructions to create your bot</li>
                            <li>Copy the token and paste it below</li>
                        </ol>
                    </div>

                    <form onSubmit={handleSubmit} className="add-bot-form card">
                        {error && <div className="auth-error">{error}</div>}

                        <div className="form-group">
                            <label className="form-label">Bot Token</label>
                            <input
                                type="text"
                                className="form-input"
                                placeholder="123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
                                value={token}
                                onChange={(e) => setToken(e.target.value)}
                                required
                                minLength={40}
                                autoFocus
                            />
                            <p className="form-hint">The token you received from @BotFather</p>
                        </div>

                        <div className="form-group">
                            <label className="form-label">Bot Name</label>
                            <input
                                type="text"
                                className="form-input"
                                placeholder="My Business Bot"
                                value={name}
                                onChange={(e) => setName(e.target.value)}
                                required
                                maxLength={100}
                            />
                            <p className="form-hint">Display name for your bot in the dashboard</p>
                        </div>

                        <div className="form-group">
                            <label className="form-label">Business Description</label>
                            <textarea
                                className="form-textarea"
                                placeholder="Describe your business, products, services, pricing, working hours, and any other relevant information that will help AI respond to customer questions..."
                                value={description}
                                onChange={(e) => setDescription(e.target.value)}
                                required
                                minLength={10}
                            />
                            <p className="form-hint">
                                This description helps AI understand your business and answer customer questions accurately
                            </p>
                        </div>

                        <div className="add-bot-actions">
                            <button
                                type="button"
                                className="btn btn-secondary"
                                onClick={() => navigate('/dashboard')}
                            >
                                Cancel
                            </button>
                            <button type="submit" className="btn btn-primary" disabled={loading}>
                                {loading ? <span className="spinner" /> : 'Add Bot'}
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    );
}
